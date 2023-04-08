import datetime
import re

import matplotlib 
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import events
import juhrnal

weekday_names= ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
month_names= ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

#
# Set the Y limits to show [0,1] nicely in case all values are zero. 
#
def set_ylim(plt, values):
    if not np.any(values):
        plt.ylim([0, +1.05])

#    
# Generate all plots related to one event type.
#
# PARAMETERS
#	event		The event
#	values		Array of values
#	date_first	Date of the first entry in the array
#
# The week starts on Monday.  Monday has index 0 in indexing. 
#
def plot_event(event, values, date_first):

    n= len(values)
    date_last= date_first + datetime.timedelta(days= n - 1)
    label= events.label_for_event(event)
    
    #
    # dv - All by day
    #
    x= np.array([date_last + datetime.timedelta(days=xx) for xx in range(-n+1,1)])
#    x= np.array(range(n))
    fig, ax= plt.subplots()
    ax.bar(x, values)
#    ax.bar(x-len(x)+1, values)
    plt.title(f'{label}, by day, full range')
    plt.xlim([x[0] - datetime.timedelta(days= 1), x[-1] + datetime.timedelta(days= 1)])
#    plt.xlim([-len(x)+1/2, 1/2])
    set_ylim(plt, values)
#    plt.xlabel('Day (0 = today)')
    plt.ylabel(events.get_ylabel(event, 'dv'))
    ax.xaxis.set_major_locator(matplotlib.dates.YearLocator(5))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y'))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/dv.{event}.pdf')
    plt.close('all')

    #
    # df - Last five years by day
    #
    n_days= round(365.25*5)
    values_last_five_years= values[(n - n_days):n]
    x= [date_last + datetime.timedelta(days=xx) for xx in range(-n_days+1, 1)]
    fig, ax= plt.subplots()
    ax.bar(x, values_last_five_years)
    plt.title(f'{label}, by day, last five years')
    plt.xlim([x[0] - datetime.timedelta(days= 1), x[-1] + datetime.timedelta(days= 1)])
    set_ylim(plt, values_last_five_years)
    plt.ylabel(events.get_ylabel(event, 'df'))
    ax.xaxis.set_major_locator(matplotlib.dates.YearLocator())
    ax.xaxis.set_minor_locator(matplotlib.dates.YearLocator(month= 7))
    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%Y'))
    ax.tick_params(axis='x', which='minor', tick1On=False, tick2On=False)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/df.{event}.pdf')
    plt.close('all')

    #
    # da - Last year by day
    #
    n_days= 365
    values_last_year= values[(n - n_days):n]
    x= [date_last + datetime.timedelta(days=xx) for xx in range(-n_days+1, 1)]
    fig, ax= plt.subplots()
    ax.bar(x, values_last_year)
    plt.title(f'{label}, by day, last year')
    plt.xlim([x[0] - datetime.timedelta(days= 1), x[-1] + datetime.timedelta(days= 1)])
    set_ylim(plt, values_last_year)
    plt.ylabel(events.get_ylabel(event, 'da'))
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax.xaxis.set_minor_locator(matplotlib.dates.MonthLocator(bymonthday= 16))
    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%b'))
    ax.tick_params(axis='x', which='minor', tick1On=False, tick2On=False)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/da.{event}.pdf')
    plt.close('all')

    #
    # dt - Last three months by day
    #
    n_days= round(365.25 / 4)
    values_last_three_months= values[(n - n_days):n]
    x= [date_last + datetime.timedelta(days=xx) for xx in range(-n_days+1, 1)]
    fig, ax= plt.subplots()
    ax.bar(x, values_last_three_months)
    plt.title(f'{label}, by day, last three months')
    plt.xlim([x[0] - datetime.timedelta(days= 1), x[-1] + datetime.timedelta(days= 1)])
    set_ylim(plt, values_last_three_months)
    plt.ylabel(events.get_ylabel(event, 'dt'))
    ax.xaxis.set_major_locator(matplotlib.dates.MonthLocator())
    ax.xaxis.set_minor_locator(matplotlib.dates.MonthLocator(bymonthday= 16))
    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%B'))
    ax.tick_params(axis='x', which='minor', tick1On=False, tick2On=False)
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/dt.{event}.pdf')
    plt.close('all')

    #
    # All starting on Monday
    #
    weekday_first= date_first.weekday()
    to_add= weekday_first
    values_from_monday= [0] * to_add + values

    #
    # Aggregate by week
    #
    weeks_unnormalized= []
    i= 0
    while i < len(values_from_monday):
        weeks_unnormalized.append(sum(values_from_monday[i:i+7]))
        i += 7
    n_weeks= len(weeks_unnormalized)
    weeks_normalized= np.array(weeks_unnormalized, dtype= float)
    weeks_normalized /= 7 
    
    #
    # dz - Aggregated by weekday
    #
    x= range(7)
    y= [0] * 7
    normalize= events.get_normalize(event, 'dz')
    if normalize:
        y= np.array(y, dtype= float)
    for i in range(7):
        b= values_from_monday[i::7]
        y[i]= sum(b)
        if normalize:
            if exclude_zeroes(event):
                y[i] /= np.count_nonzero(b)  
            else:
                y[i] /= len(b)
    fig, ax= plt.subplots()
    ax.bar(x, y)
    plt.title(f'{label}, by weekday')
    plt.xlim([-1/2, 7-1/2])
    plt.ylabel(events.get_ylabel(event, 'dz'))
    plt.xticks(x, weekday_names)
    if not normalize:
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/dz.{event}.pdf')
    plt.close('all')
    
    #
    # wv - All by week
    #
    x= np.array(range(n_weeks))
    y= weeks_normalized if events.get_normalize(event, 'wv') else weeks_unnormalized
    fig, ax= plt.subplots()
    ax.bar(x-len(x)+1, y)
    plt.title(f'{label}, by week, full range')
    plt.xlim([-len(x)+1/2, 1/2])
    set_ylim(plt, y)
    plt.xlabel('Week (0 = this week)')
    plt.ylabel(events.get_ylabel(event, 'wv'))
    if not events.get_normalize(event, 'wv'):
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/wv.{event}.pdf')
    plt.close('all')

    #
    # wf - Last five years by week
    #
    y= weeks_normalized if events.get_normalize(event, 'wf') else weeks_unnormalized
    y= y[(n_weeks-round(365.25*5/7)):n_weeks]
    x= np.array(range(len(y)))
    fig, ax= plt.subplots()
    ax.bar(x-len(x)+1, y)
    plt.title(f'{label}, by week, last five years')
    plt.xlim([-len(x)+1/2, 1/2])
    set_ylim(plt, y)
    plt.xlabel('Week (0 = this week)')
    plt.ylabel(events.get_ylabel(event, 'wf'))
    if not events.get_normalize(event, 'wf'):
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/wf.{event}.pdf')
    plt.close('all')

    #
    # wa - Last year by week
    #
    y= weeks_normalized if events.get_normalize(event, 'wa') else weeks_unnormalized
    y= y[(n_weeks-round(365.25/7)):n_weeks]
    x= np.array(range(len(y)))
    fig, ax= plt.subplots()
    ax.bar(x-len(x)+1, y)
    plt.title(f'{label}, by week, last year')
    plt.xlim([-len(x)+1/2, 1/2])
    set_ylim(plt, y)
    plt.xlabel('Week (0 = this week)')
    plt.ylabel(events.get_ylabel(event, 'wa'))
    if not events.get_normalize(event, 'wa'):
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/wa.{event}.pdf')
    plt.close('all')

    #
    # Aggregate by month
    #
    months_unnormalized= []
    months_lens= [] # Length in days of each month
    months_nonzero= [] # Number of days with nonzeroes in each month
    d= datetime.date(year= date_first.year, month= date_first.month, day= 1)
    d_last= datetime.date(year= date_last.year, month= date_last.month, day= 1)
    while d <= d_last:
        d_next_year= d.year
        d_next_month= d.month
        d_next_month += 1
        if d_next_month > 12:
            d_next_year += 1
            d_next_month= 1
        d_next= datetime.date(year= d_next_year, month= d_next_month, day= 1)
        i_1= (d - date_first).days
        i_2= (d_next - date_first).days
        months_unnormalized.append(sum(values[i_1:i_2]))
        months_lens.append((d_next - d).days)
        months_nonzero.append(np.count_nonzero(values[i_1:i_2]))
        d= d_next
    months_lens[-1] -= (d_next - date_last).days - 1 # Last month is not complete
    n_months= len(months_unnormalized)
    months_normalized= np.array(months_unnormalized, dtype= float)
    months_normalized /= months_lens

    #
    # mv - All by month
    #
    x= np.array(range(n_months))
    y= months_normalized if events.get_normalize(event, 'mv') else months_unnormalized
    fig, ax= plt.subplots()
    ax.bar(x-len(x)+1, y)
    plt.title(f'{label}, by month, full range')
    plt.xlim([-len(x)+1/2, 1/2])
    set_ylim(plt, y)
    plt.xlabel('Month (0 = this month)')
    plt.ylabel(events.get_ylabel(event, 'mv'))
    if not events.get_normalize(event, 'mv'):
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/mv.{event}.pdf')
    plt.close('all')

    #
    # mf - Last five years by month
    #
    y= months_normalized if events.get_normalize(event, 'mf') else months_unnormalized
    y= y[(n_months-12*5):n_months]
    x= np.array(range(len(y)))
    fig, ax= plt.subplots()
    ax.bar(x-len(x)+1, y)
    plt.title(f'{label}, by month, last five years')
    plt.xlim([-len(x)+1/2, 1/2])
    set_ylim(plt, y)
    plt.xlabel('Month (0 = this month)')
    plt.ylabel(events.get_ylabel(event, 'mf'))
    if not events.get_normalize(event, 'mf'):
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/mf.{event}.pdf')
    plt.close('all')

    #
    # ma - Last year by month
    #
    ma_months= 13 # Show last 13 to always have 12 full months in the plot
    y= months_normalized if events.get_normalize(event, 'ma') else months_unnormalized
    y= y[(n_months - ma_months):n_months]
    x= np.array(range(len(y)))
    fig, ax= plt.subplots()
    ax.bar(x-len(x)+1, y)
    plt.title(f'{label}, by month, last year')
    plt.xlim([-len(x)+1/2, 1/2])
    set_ylim(plt, y)
    plt.ylabel(events.get_ylabel(event, 'ma'))
    month_names_shifted= [''] * ma_months
    for i in range(ma_months):
        month= (date_last.month + i - ma_months) % 12
        name= month_names[month]
        if i == 0:
            name += f'\n{date_last.year - 1}'
        elif month == 0:
            name += f'\n{date_last.year}'
        month_names_shifted[i]= name
    plt.xticks(x-len(x)+1, month_names_shifted)
    if not events.get_normalize(event, 'ma'):
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/ma.{event}.pdf')
    plt.close('all')

    #
    # mz - By month of the year
    #
    month_first= date_first.month
    to_add= month_first - 1
    months_unnormalized_from_january= np.concatenate(([0] * to_add, months_unnormalized))
    months_lens_from_january= np.concatenate(([0] * to_add, months_lens))
    months_nonzero_from_january= np.concatenate(([0] * to_add, months_nonzero))
    x= range(12)
    y= [0] * 12
    normalize= events.get_normalize(event, 'mz')
    if normalize:
        y= np.array(y, dtype= float)
    for i in range(12):
        b= months_unnormalized_from_january[i::12]
        y[i]= sum(b)
        if normalize:
            if exclude_zeroes(event):
                y[i] /= sum(months_nonzero_from_january[i::12])
            else:
                y[i] /= sum(months_lens_from_january[i::12])
    fig, ax= plt.subplots()
    ax.bar(x, y)
    plt.title(f'{label}, by month of the year')
    plt.xlim([-1/2, 12-1/2])
    plt.ylabel(events.get_ylabel(event, 'mz'))
    plt.xticks(x, month_names)
    if not events.get_normalize(event, 'mz'):
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/mz.{event}.pdf')
    plt.close('all')

    #
    # Aggregate by year
    #
    years_unnormalized= []
    years_lens= []
    d= datetime.date(year= date_first.year, month= 1, day= 1)
    d_last= datetime.date(year= date_last.year, month= 1, day= 1)
    while d <= d_last:
        d_next= datetime.date(year= d.year + 1, month= 1, day= 1)
        i_1= (d - date_first).days
        i_2= (d_next - date_first).days
        years_unnormalized.append(sum(values[i_1:i_2]))
        years_lens.append((d_next - d).days)
        d= d_next
    years_lens[-1] -= (d_next - date_last).days - 1 # last year is not complete
    n_years= len(years_unnormalized)
    years_normalized= np.array(years_unnormalized, dtype= float)
    years_normalized /= years_lens
    
    #
    # av - All by year
    #
    x= np.array(range(n_years))
    y= years_normalized if events.get_normalize(event, 'av') else years_unnormalized
    fig, ax= plt.subplots()
    ax.bar(x + date_first.year, y)
    plt.title(f'{label}, by year, full range')
    plt.xlim([date_first.year - 1/2, date_last.year + 1/2])
    set_ylim(plt, y)
    plt.ylabel(events.get_ylabel(event, 'av'))
    if not events.get_normalize(event, 'av'):
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig(f'plot/av.{event}.pdf')
    plt.close('all')

def plot_histograms(j: juhrnal.Juhrnal):

    #
    # All (x) medical problems
    # 
    m= []
    for event in j.intensities_by_index_by_event:
        if not re.compile('\([a-zα-ω]\)').fullmatch(event):  continue
        m.append({'event': event, 'value': sum(j.intensities_by_index_by_event[event])})
    n= len(m)
    m.sort(key= lambda x: x.get('value'), reverse= True)
    x= range(n)
    y= [0] * n
    ticks= [''] * n
    for i in x:
        y[i]= m[i]['value']
        ticks[i]= re.sub('\((.*)\)', '\\1', m[i]['event'])
    fig, ax= plt.subplots()
    ax.bar(x, y)
    plt.title('Medical problems by intensity sum')
    plt.xlim([-1/2, n-1/2])
    plt.ylabel('Intensity sum')
    plt.xticks(x, ticks)
    plt.savefig('plot/hist.problems.pdf')
    plt.close('all')

    #
    # All #tags
    # 
    m= []
    for event in j.intensities_by_index_by_event:
        if not event[0] == '#':  continue
        if event == '#all': continue
        m.append({'event': event, 'value': sum(j.intensities_by_index_by_event[event])})
    n= len(m)
    m.sort(key= lambda x: x.get('value'), reverse= True)
    x= range(n)
    y= [0] * n
    ticks= [''] * n
    for i in x:
        y[i]= m[i]['value']
        ticks[i]= m[i]['event']
    fig, ax= plt.subplots()
    ax.bar(x, y)
    plt.title('Products by count')
    plt.xlim([-1/2, n-1/2])
    plt.ylabel('Count')
    plt.xticks(x, ticks, rotation= -20, fontsize= 'small', \
               rotation_mode= 'anchor', horizontalalignment= 'left')
    plt.savefig('plot/hist.products.pdf')
    plt.close('all')

    #
    # All @X measurements
    # 
    m= []
    for event in j.intensities_by_index_by_event:
        if not event[0] == '@':  continue
        m.append({'event': event, 'value': sum(j.intensities_by_index_by_event[event])})
    n= len(m)
    m.sort(key= lambda x: x.get('value'), reverse= True)
    x= range(n)
    y= [0] * n
    ticks= [''] * n
    for i in x:
        y[i]= m[i]['value']
        ticks[i]= m[i]['event']
    fig, ax= plt.subplots()
    ax.bar(x, y)
    plt.title('Measurements by count')
    plt.xlim([-1/2, n-1/2])
    plt.ylabel('Count')
    plt.xticks(x, ticks)
    plt.savefig('plot/hist.measurements.pdf')
    plt.close('all')

def plot_measurements(j: juhrnal.Juhrnal):

    #
    # @P - Pressure
    #
    n= len(j.pressures)
    x= [0] * n
    ys= [0] * n
    yd= [0] * n
    for i in range(n):
        x[i]= j.pressures[i][0]
        ys[i]= j.pressures[i][1]
        yd[i]= j.pressures[i][2]
    x= np.array(x) - j.n_days + 1

    # @P.time
    fig, axarr= plt.subplots(2, sharex= True)
    axarr[0].plot(x, ys, 'go', alpha= 0.2)
    axarr[1].plot(x, yd, 'bo', alpha= 0.2)
    axarr[0].set_title('Pressure measurements by day')
    plt.xlim([x[0] - 1/2, 1/2])
    axarr[1].set_xlabel('Day (0 = today)')
    axarr[0].set_ylabel('Systolic [mmHg]')
    axarr[1].set_ylabel('Diastolic [mmHg]')
    plt.savefig('plot/measurements.@P.time.pdf')
    plt.close('all')

    # @P.scatter
    fig, ax= plt.subplots()
    ax.plot(yd, ys, 'o', alpha= 0.1)
    plt.title('Pressure measurements, scatter plot')
    plt.xlabel('Diastolic [mmHg]')
    plt.ylabel('Systolic [mmHg]')
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer= True))
    plt.savefig('plot/measurements.@P.scatter.pdf')
    plt.close('all')

    #
    # @R - Heart rate
    #
    n= len(j.rates)
    x= np.zeros(n)
    y= np.zeros(n)
    for i in range(n):
        x[i]= j.rates[i][0]
        y[i]= j.rates[i][1]
    x -= j.n_days - 1
    
    # @R.time
    fig, ax= plt.subplots()
    ax.plot(x, y, 'o')
    plt.title('Heart rate measurements by day')
    plt.xlabel('Day (0 = today)')
    plt.ylabel('Heart rate [bpm]')
    plt.savefig('plot/measurements.@R.time.pdf')
    plt.close('all')

    #
    # @W+@F - Weight and fat percentage
    #
    xw= [e[0] - j.n_days + 1 for e in j.measurements['W']]
    yw= [e[1] for e in j.measurements['W']]
    xf= [e[0] - j.n_days + 1 for e in j.measurements['F']]
    yf= [e[1] for e in j.measurements['F']]

    # @W.time
    fig, axarr= plt.subplots(2, sharex= True)
    axarr[0].plot(xw, yw, 'go')
    axarr[1].plot(xf, yf, 'bo')
    axarr[0].set_title('Weight measurements by day')
    plt.xlim([min([xw[0], xf[0]]) - 1/2, 1/2])
    axarr[1].set_xlabel('Day (0 = today)')
    axarr[0].set_ylabel('Body weight [kg]')
    axarr[1].set_ylabel('Body fat [%]')
    plt.savefig('plot/measurements.@W.time.pdf')
    plt.close('all')

    #
    # @E - Eye test
    #
    n= len(j.eyetests)
    x=                 np.zeros(n)
    right_spherical=   np.zeros(n)
    right_cylindrical= np.zeros(n)
    right_axis=        np.zeros(n)
    left_spherical=    np.zeros(n)
    left_cylindrical=  np.zeros(n)
    left_axis=         np.zeros(n)
    for i in range(n):
        x[i]=                 j.eyetests[i][0]
        right_spherical[i]=   j.eyetests[i][1]
        right_cylindrical[i]= j.eyetests[i][2]
        right_axis[i]=        j.eyetests[i][3]
        left_spherical[i]=    j.eyetests[i][4]
        left_cylindrical[i]=  j.eyetests[i][5]
        left_axis[i]=         j.eyetests[i][6]
    x= x - j.n_days + 1
    right_sum= right_spherical + right_cylindrical
    left_sum = left_spherical  + left_cylindrical
    right_axis -= 180

    # @E.time
    fig, axarr= plt.subplots(4, sharex= True)
    axarr[0].plot(x[left_cylindrical != 0], left_axis[left_cylindrical != 0],         'r.')
    axarr[1].plot(x, left_sum,          'ro')
    axarr[1].plot(x, 0.5 * (left_sum + left_spherical),   '-r')
    axarr[1].plot(x, left_spherical,    'ro')
    axarr[2].plot(x, right_spherical,   'go')
    axarr[2].plot(x, 0.5 * (right_sum + right_spherical), '-g')
    axarr[2].plot(x, right_sum,         'go')
    axarr[3].plot(x[right_cylindrical != 0], right_axis[right_cylindrical != 0],        'g.')
    axarr[0].set_title('Eye tests by day')
    xdist= 0.05 * (x[-1] - x[0])
    plt.xlim([x[0] - xdist, x[-1] + xdist])
    all_min= min(min(right_sum), min(left_sum), min(right_spherical), min(left_spherical))
    all_max= max(max(right_sum), max(left_sum), max(right_spherical), max(left_spherical))
    all_delta= all_max - all_min
    all_min -= 0.2 * all_delta
    all_max += 0.2 * all_delta
    all_max= min(0, all_max)
    axarr[1].set_ylim([all_min, all_max])
    axarr[2].set_ylim([all_min, all_max])
    axis_min= min(min(left_axis[left_cylindrical != 0]), min(-right_axis[left_cylindrical != 0]))
    axis_max= max(max(left_axis[left_cylindrical != 0]), max(-right_axis[left_cylindrical != 0]))
    axis_delta= axis_max - axis_min
    axarr[0].set_ylim([axis_min - 0.2 * axis_delta, axis_max + 0.2 * axis_delta])
    axarr[3].set_ylim([-axis_max - 0.2 * axis_delta, -axis_min + 0.2 * axis_delta])
    axarr[3].set_xlabel('Day (0 = today)')
    axarr[0].set_ylabel('L ax [°]')
    axarr[1].set_ylabel('L [m¯¹]')
    axarr[2].set_ylabel('R [m¯¹]')
    axarr[3].set_ylabel('R ax [°]')
    axarr[1].invert_yaxis()
    plt.savefig('plot/measurements.@E.time.pdf')
    plt.close('all')
    
# Determines whether we exclude days with zero values from normalization.  
def exclude_zeroes(event):
    return event[0] == '$'
