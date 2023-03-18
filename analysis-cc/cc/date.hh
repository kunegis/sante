#ifndef DATE_HH
#define DATE_HH

/*
 * Values are -1 when unknown.  If a component is known, all subsequent ones are
 * known. 
 *
 * Months and days are 1-based.
 */
struct Date
{
	int year;
	int month;
	int day;

	Date(int _year, int _month, int _day) 
		:  year(_year), month(_month), day(_day)
	{
		assert(year >= -1);
		assert(year < 10000);
		assert(month >= -1);
		assert(month != 0); 
		assert(month <= 12);
		assert(day >= -1);
		assert(day != 0); 
		assert(day <= 31);
		assert(month >= 0 || day == -1); 
	}

	bool operator==(Date date) const
	{
		return year == date.year && month == date.month && day == date.day; 
	}

	bool operator<=(Date date) const
	{
		assert(has_day());
		assert(date.has_day()); 
		return year < date.year || month < date.month || day <= date.day;
	}
	
	bool has_day() const {
		return day >= 0;
	}

	/* Make all components defined by assuming they are equal to one. */
	void fill() {
		if (month < 0) {
			month= 1;
			day= 1;
		} else if (day < 0) {
			day= 1; 
		}
	}
};

int days_in_month(int year, int month)
{
	assert(year > 0);
	assert(month >= 1 && month <= 12);

	switch (month) {
	case 1:  case 3:  case 5:  case 7:  case 8:  case 10:  case 12:
		return 31;
	case 4:  case 6:  case 9:  case 11:
		return 30;
	case 2:
		if (year % 4)
			return 28;
		if (year / 4 % 25)
			return 29;
		if (year / 100 % 4)
			return 28;
		return 29;
	}

	assert(false);
	return -1;
}

/* The next day */
Date date_next(Date date)
{
	assert(date.has_day()); 

	++ date.day;

	if (date.day > days_in_month(date.year, date.month)) {
		++ date.month;
		date.day= 1;
	}

	if (date.month > 12) {
		++ date.year;
		date.month= 1; 
	}

	return date;
}

class Date_Diff_Calculator
{
public:
	Date_Diff_Calculator(Date _date_begin)
		:  date_begin(_date_begin),
		   offset(0)
	{
		assert(date_begin.has_day());
		offset -= (date_begin.day - 1);
		date_begin.day= 1;
	}

	int diff(const Date date)
	{
		assert(date.has_day());
		assert(date_begin.day == 1); 
		assert(date_begin.year <= date.year);
		assert(date_begin.year < date.year
		       || date_begin.month <= date.month);
		assert(date_begin.year < date.year || date_begin.month < date.month
		       || date_begin.day <= date.day);

		while (date_begin.year < date.year || date_begin.month < date.month) {
			int days= days_in_month(date_begin.year, date_begin.month);
			offset += days;
			++ date_begin.month;
			if (date_begin.month == 13) {
				++ date_begin.year;
				date_begin.month= 1; 
			}
		}

		assert(date_begin.year  == date.year);
		assert(date_begin.month == date.month);

		return offset + date.day - date_begin.day; 
	}

	/* Return what is effectively B - A */
	static int diff(Date a, Date b) {
		Date_Diff_Calculator ddc(a);
		return ddc.diff(b); 
	}
	
private:
	/* Calculate the date from DATE_BEGIN, always adding OFFSET days.
	 * DATE_BEGIN.DAY is always kept at one.  */
	Date date_begin;
	int offset; 
};

#endif /* ! DATE_HH */
