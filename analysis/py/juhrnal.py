import re
import datetime 

import numpy as np

import events
import os
import sys

class Juhrnal:

    # Key is the date index; values are texts
    texts_by_index= []

    # Key is the event letter; values are arrays of length N_DAYS whose index is
    # the date index, and whose values are sums are maximal intensities for the
    # day.  The keys in this member also serve as the canonical source for the
    # set of events.  
    intensities_by_index_by_event= {}

    # The date of the first day
    date_first= None

    # The number of days
    n_days= -1

    # @P.  Triples of:  (index, systolic, diastolic)
    pressures= []

    # @R.  Pairs of:  (index, heart_rate)
    rates= []

    # @E.  Heptuples of index and the six variables in same order as in the event
    eyetests= []

    # Other measurements.  Keys are measures (without @); values are arrays of
    # tuples: (index, value).  
    measurements= {}

    filename= ""
    line_count= 0
    
    def add_event(self, index, event, intensity= 1):
        assert(type(intensity) == int)
        if not event in self.intensities_by_index_by_event:
            self.intensities_by_index_by_event[event]= []
        while len(self.intensities_by_index_by_event[event]) <= index:
            self.intensities_by_index_by_event[event].append(0)
        assert len(self.intensities_by_index_by_event[event]) > index
        self.intensities_by_index_by_event[event][index] += intensity

    # MEASURE is the name without '@'.  
    def add_measurement(self, measure, index, value):
        assert(type(value) == int or type(value) == float)
        if not measure in self.measurements:
            self.measurements[measure]= []
        self.measurements[measure].append((index, value))
        
    def __init__(self, filename= 'sante/JUHRNAL'):
        self.filename= filename
        file= open(filename, 'r')
        has_first= False
        text_last_night= ''
        index= 0

        while True:
            line= file.readline()
            if not line:  break
            self.line_count += 1;
            line= re.sub('\n', '', line)
            if re.compile('\s*').fullmatch(line):  continue
            line= line.expandtabs()

            m= re.compile('night      (.*)').fullmatch(line)
            if m:
                text_last_night= m.group(1);
                continue

            m= re.compile('([0-9]{4})(      |-([0-9]{2})(  |-([0-9]{2})))(| (.*))').fullmatch(line)
            if not m:
                self.raise_error('Invalid date')

            text_year = m.group(1)
            text_month= m.group(3)
            text_day  = m.group(5)
            text      = m.group(7)
            
            year = int(text_year )
            month= int(text_month) if text_month else 1
            day  = int(text_day  ) if text_day   else 1
            if not text:  text= ''

            date_this= datetime.date(year= year, month= month, day= day)
            if not has_first:
                self.date_first= date_this
                has_first= True
            index= (date_this - self.date_first).days

            if text_last_night != '':
                text= text_last_night + ' ' + text
                text_last_night= ''

            while len(self.texts_by_index) < index:
                self.texts_by_index.append('')
            # Check that date of line is not before date of an earlier line 
            if len(self.texts_by_index) != index:
                self.raise_error('Date is earlier or equal to a previous date')
            self.texts_by_index.append(text)

            #
            # (*)
            #
            for mm in re.compile('\(([^)]*)\)').findall(text):
                text_inner= mm
                mmm= re.compile('([0-9]*)([^0-9)])').fullmatch(text_inner)
                if not mmm:
                    self.raise_error('Syntax error in event ({text_inner})')
                text_intensity  = mmm.group(1)
                event_underlying= mmm.group(2)
                event= f'({event_underlying})'
                if event_underlying == 'A':
                    self.raise_error('Event (A) is not allowed')
                intensity= 1
                if text_intensity != '':  intensity= int(text_intensity)
                self.add_event(index, event, intensity)

            #
            # [*]
            #
            for mm in re.compile('\[([^0-9()])\]').findall(text):
                event_underlying= mm[0]
                event= f'[{event_underlying}]'
                self.add_event(index, event)

            #
            # #tags
            #
            for mm in re.compile('#(\w+)(\W|$)').findall(text):
                tag= mm[0]
                if tag == 'all':  self.raise_error('Tag #all is not allowed')
                events.check_tag(tag)
                event= f'#{tag}'
                self.add_event(index, event)

            #
            # @
            #
            for text_inner in re.compile('@([^@]*)@').findall(text):
                mm= re.compile('([A-Z])=([^@]+)').fullmatch(text_inner)
                if not mm:
                    self.raise_error(f'Syntax error in measurement @{text_inner}@')
                measure= mm.group(1)
                value  = mm.group(2)
                event= f'@{measure}'
                self.add_event(index, event)
                if measure == 'P':
                    n= re.compile('([0-9]+)/([0-9]+)').fullmatch(value)
                    if not n:
                        self.raise_error(f'Invalid pressure measurement "{value}"')
                    systolic = int(n.group(1))
                    diastolic= int(n.group(2))
                    self.pressures.append((index, systolic, diastolic))
                elif measure == 'R':
                    n= re.compile('([0-9]+)').fullmatch(value)
                    if not n:
                        self.raise_error(f'Invalid heart rate measurement "{value}"')
                    rate= int(n.group(1))
                    self.rates.append((index, rate))
                elif measure == 'E':
                    n= re.compile('([-0-9.]+),([-0-9.]+),([-0-9.]+);([-0-9.]+),([-0-9.]+),([-0-9.]+)').fullmatch(value)
                    if not n:
                        self.raise_error(f'Invalid eye measurement "{value}"')
                    right_spherical=   float(n.group(1))
                    right_cylindrical= float(n.group(2))
                    right_axis=        float(n.group(3))
                    left_spherical=    float(n.group(4))
                    left_cylindrical=  float(n.group(5))
                    left_axis=         float(n.group(6))
                    self.eyetests.append((index,
                                          right_spherical, right_cylindrical, right_axis,
                                          left_spherical,  left_cylindrical,  left_axis))
                else:
                    # Check that the measure exists
                    unused= events.label_for_event(f'@{measure}')
                    factor= 1
                    if value[-1] == '%':
                        factor= 100
                        value= value[:-1]
                    n= re.compile('[0-9]+(|\.[0-9]+)').fullmatch(value)
                    if not n:
                        self.raise_error(f'Invalid measurement value in "{text_inner}"')
                    value= float(value)
                    self.add_measurement(measure, index, value)
                
            #
            # Proscribed patterns
            #
            if text.count('@') % 2 != 0:
                self.raise_error('"@" must appear an even number of times in each line')
                
        file.close()

        #
        # Tracker data
        #
        filenames= os.listdir('dat')
        for filename in filenames:
            m= re.compile('tracker\.([a-z]*)').fullmatch(filename)
            if not m:  continue
            name= m.group(1)
            file= open(f'dat/{filename}', 'r')
            while True:
                line= file.readline()
                if not line:  break
                line= re.sub('\n', '', line)
                if re.compile('[:space:]*').fullmatch(line):  continue
                m= re.compile('^([0-9]{4})-([0-9]{2})-([0-9]{2})\s+([0-9]+)$').fullmatch(line)
                if not m:
                    self.raise_error(f'Invalid tracker line "{line}"')
                text_year = m.group(1)
                text_month= m.group(2)
                text_day  = m.group(3)
                text      = m.group(4)
                year = int(text_year )
                month= int(text_month)
                day  = int(text_day  )
                date_this= datetime.date(year= year, month= month, day= day)
                if not has_first:
                    self.date_first= date_this
                    has_first= True
                index= (date_this - self.date_first).days
                assert(index >= 0)
                event= f'${name}'
                intensity= int(text)
                self.add_event(index, event, intensity)
            file.close()
        
        # Fill the end of all arrays with zero
        index= (datetime.date.today() - self.date_first).days
        self.n_days= index + 1
        if len(self.texts_by_index) < self.n_days:
            self.texts_by_index += [''] * (self.n_days - len(self.texts_by_index))

        self.intensities_by_index_by_event['(&)']= list(map(len, self.texts_by_index))

        for event in self.intensities_by_index_by_event:
            if len(self.intensities_by_index_by_event[event]) < self.n_days:
                self.intensities_by_index_by_event[event] += \
                    [0] * (self.n_days - len(self.intensities_by_index_by_event[event]))

        #
        # Aggregated events:  {A}, #all
        #
        intensities_A= np.array([0] * self.n_days)
        for event in self.intensities_by_index_by_event:
            m= re.compile('\([a-zα-ω]\)').fullmatch(event)
            if m:
                intensities_A += self.intensities_by_index_by_event[event]
        self.intensities_by_index_by_event['{A}']= list(intensities_A)

        intensities_all= np.array([0] * self.n_days)
        for event in self.intensities_by_index_by_event:
            m= re.compile('#\w+').fullmatch(event)
            if m:
                intensities_all += self.intensities_by_index_by_event[event]
        self.intensities_by_index_by_event['#all']= list(intensities_all)

        #
        # Other aggregated events
        #
        for aggregate_event in events.aggregate_events():
            a= np.array([0] * self.n_days)
            subevents= events.subevents(aggregate_event)
            for subevent in subevents:
                a += self.intensities_by_index_by_event[subevent]
            self.intensities_by_index_by_event[aggregate_event]= list(a)

    def raise_error(self, text):
        print(f'\n{self.filename}:{self.line_count}: {text}', file= sys.stderr)
        sys.exit(1)
