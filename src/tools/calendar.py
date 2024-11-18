""" 
A collection of functions and classes that make it easy to work with 
dates (basically a simplification of the datetime package) and to
display a calendar in matplotlib.
"""

import datetime
import warnings

import numpy as np 
import matplotlib as mpl 
import matplotlib.pyplot as plt 

from .array import find_contours 

# This should probably not be here, but instead be called by the user
import locale
locale.setlocale(locale.LC_TIME, 'de_DE')

__all__ = ["to_date","last_day_of_month","range_of_dates","Date",
           "DayCalendar","WeekCalendar","MonthCalendar","YearCalendar"]


def to_date(*date,format=r'%Y-%m-%d'):
    """Convert a variety of formats to datetime.date.
    
    Parameter
    ---------
    *date : date or datetime or list of int or tuple of int  or str
        Three integers are interpreted as year, month and day.
        If the parameter is of type `datetime.date`, it is returned by 
        itself. In the case of `datetime.datetime`, the date method will 
        be applied. A list or tuple of integers will be treated like 
        year, month, date. A string is interpreted according the 
        specified format.  
    format : str, optional
        Format of the date when passed as a string. The default is 
        '%Y-%m-%d', corresponding to 'year-month-day'.
        
    Returns
    -------
    datetime.date
    """

    if len(date)==3:
        # three args are assumed to be year, month, day
        return datetime.date(*date)
    else: 
        # the * in the arguments turns arg into (arg,)
        date = date[0]
      
    # date is an instance of datetime but datetime is no instance of date
    if isinstance(date,datetime.datetime):
        return date.date()
    elif isinstance(date,datetime.date):
        return date
    elif isinstance(date,(list,tuple)):
        return datetime.date(*date)
    elif isinstance(date,str):
        # this function returns datetime and we convert it to date
        return datetime.datetime.strptime(date,format).date()
    else:
        raise ValueError(f'unkown dtype/format for {date}')


def last_day_of_month(*date):
    """Calculate the last day of the month.
    
    In principal, one could simply get the result from the following list 
        [31,29,31,30,31,30,31,31,30,31,30,31]
    However this is not true for years with a leap day. In order to 
    account for that, we replace the day of the date to 1, add 32 days
    to land in the next month, replace the day again to 1 to get to the
    first day and finally subtract 1 to get to the last day of the 
    current month.
    
    Parameters
    ----------
    date : datetime
    
    Returns
    -------
    date
        The date of the last day in the month.
    """
    
    date = to_date(*date)
    return (date.replace(day=1) + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)


def range_of_dates(
        start_date=None,
        end_date=None,
        ndays=None,
        format=r'%Y-%m-%d',
        return_string=False):
    """Create a list of dates.
    
    Parameters
    ----------
    start_date : datetime.date or str in format
        The first day in the list. If `None`, the day is calculated based
        on ndays or as the beginning of the current month.
    end_date : datetime.date or str in format
        The last day in the list. If `None`, the day is calculated based
        on ndays or as the ending of the current month.
    ndays : int
        The number of days in the returned list. Only used if start_date
        or end_date are missing. If negative we go backwards.
    format : str (default "%Y-%m-%d")
        Used when start_date or end_date are in string format.
    return_string : bool
        Apply strftime(format) to the returned values.
    """
    
    # we pass the input to `to_date` to get a datetime.date object
    if start_date is not None:
        start_date = to_date(start_date,format)
    if end_date is not None:
        end_date = to_date(end_date,format)

    if start_date:
        if end_date:
            # we need ndays +- 1 steps depending on the direction
            difference = (end_date - start_date).days
            ndays = int(difference + difference/abs(difference))
        elif ndays:
            # we go forward ndays
            pass
        else: 
            # with neither end_date and ndays we use the last day of the month as end_date
            end_date = last_day_of_month(start_date)
            difference = (end_date - start_date).days
            ndays = int(difference + difference/abs(difference))
            
    elif end_date:
        if ndays:
            # we need ndays +- 1 steps depending on the direction
            start_date = end_date - datetime.timedelta(days=int(ndays-ndays/abs(ndays)))
        else:
            # with neither start_date and ndays we use the first day of the month as start_date
            start_date = end_date.replace(day=1)
            ndays = (end_date - start_date).days + 1
            
    else:
        raise ValueError('either start_date or end_date required')

    # the direction is based on the sign of ndays
    direction = int(ndays/abs(ndays))
    dates = [start_date+datetime.timedelta(days=n) for n in range(0,ndays,direction)]   
    
    if return_string:
        return [date.strftime(format) for date in dates]
    else:
        return dates
    

# The class datetime.date takes year, month and day as parameters to 
# construct a new object. 
# https://github.com/python/cpython/blob/main/Lib/_pydatetime.py
# However, there are a few more formats that I regularly use to define a 
# date. For this purpose, the function `to_date` can recognizes them and 
# return a matching datetime.date object. In the following, we add this 
# functionality directly to a new subclass of datetime.date. Because the 
# subclass is a child of an immutable class, we need to redefine the 
# __new__ function
# https://stackoverflow.com/questions/399022/why-cant-i-subclass-datetime-date

class Date(datetime.date):
    """Wrapper for datetime.date.
    
    This class calls the function `to_date` to convert different input 
    formats into a datetime.date format. In addition, the methods for 
    __add__ and __subtract__ are modified to accept int as an input. 
    """
    
    def __new__(cls,*args):
        date = to_date(*args)
        return super().__new__(cls,date.year,date.month,date.day)

    def __add__(self,other):
        """Add timedelta or days from Date
        
        Parameters
        ----------
        other : timedelta or int
            The second term of the addition is either a timedelta object
            or an integer in units of days.
        
        Returns 
        -------
        Date
        """
        if isinstance(other,datetime.timedelta):
            return super().__add__(other)
        elif isinstance(other,int):
            return super().__add__(datetime.timedelta(other))
        return NotImplemented
    
    __radd__ = __add__
    
    def __sub__(self,other):
        """Subtract date, timedelta or days from Date
        
        Parameters
        ----------
        other : date, timedelta or int
            If other is a date, the difference between the two is 
            calculated and returned as a timedelta. If other is an
            integer, it is assumed to be in units of dates and converted 
            into a timedelta objects. Subtracting those from the Date
            returns a new Date.
        
        Returns
        -------
        Date or timedelta
            Subtraction between two dates returns the difference in days
            while subtracting timedelta returns a new Date.
        """
        
        # I personally prefer to get timedelta.days() instead of 
        # timedelta. However this might cause errors if the object Dates
        # is used in other functions that apply a subtraction. Therefore
        # the returned result remains a timedelta.
        
        if isinstance(other,(datetime.timedelta,datetime.date)):
            return super().__sub__(other)
        elif isinstance(other,int):
            return super().__sub__(datetime.timedelta(other))
        return NotImplemented
    
  
class DayCalendar:
    
    def __init__(self,start_date,end_date,firstweekday=0):
        """ 
        This is a minimalistic example for a date grid.
        
        Parameters
        ----------
        start_date : datetime.date
            The first day in the calendar.
        end_date : datetime.date
            The last day in the calendar.
        firstweekday : int
            From 0 (Monday) to 6 (Sunday).
        """
        
        self.start_date = to_date(start_date) 
        self.end_date = to_date(end_date)
        self.ndays = (self.end_date-self.start_date).days + 1
        self.firstweekday = firstweekday
        
        # we create a list of all dates and places to store further input
        # we turn it into a 2d array to utilize generate_image().
        self.dates = np.array([start_date+datetime.timedelta(days) for days in range(self.ndays)]).reshape(1,-1)
        self.events = dict()
        self.colors = dict()
        
    def add_event(self,date,event=1,format=r'%Y-%m-%d'):    
        """
        Add value to the events array at the given date.This method 
        overwrites existing values.
        
        Parameters
        ----------
        date : datetime.date | tuple | list
            The tuple/list (year,month,day) is parsed as date(*tuple).
        event : object 
            Can be any object and is stored under self.events[date] = event.
        format : str
            The format of the date if a string is passed.
        """
        
        # convert datetime or str to date
        date = to_date(date,format=format)
            
        # we only date of type datetime.date to the dictionary
        if isinstance(date,datetime.date):
            if self.start_date<=date<=self.end_date:
                self.events[date] = event
            else:
                warnings.warn(f"{date.strftime(r'%Y-%m-%d')} lies outside.")

    def update_colors(self,color_dict=None,cmap='Wistia'):
        """ 
        Update the colors dictionary based on the events dictionary.
        """
        
        unique_events = set(self.events.values())
        if not color_dict:
            color_dict = {}
            cmap = plt.get_cmap(cmap,len(unique_events))
            # convert rgba to hex
            color_dict = {event:f'#{int(255*cmap(i)[0]):02x}{int(255*cmap(i)[1]):02x}{int(255*cmap(i)[2]):02x}' 
                            for i,event in enumerate(unique_events)}
        for date, event in self.events.items():
            self.colors[date] = color_dict.get(event,'#000000')
            
        
    def generate_image(self):
        """ 
        Turn the colors dictionary into an 3d array that contains two
        spatial dimensions and a third one for the rgb values.
        """
        
        # we start by creating a 2d array with the hex values
        hex2d = np.empty(self.dates.shape,dtype='U7')
        for date, hex in self.colors.items():
            hex2d[self.dates==date] = hex
        
        # then we add a dimension and convert hex to rgb
        rgb3d = np.full(hex2d.shape+(3,),np.nan)
        for hex_string in np.unique(hex2d):
            if hex_string.startswith('#'):
                rgb3d[hex2d==hex_string] = tuple(int(hex_string[i+1:i+3],16)/255  for i in (0, 2, 4)) 

        return rgb3d

    def plot(self,ax=None):
        """
        A simple example how to showcase the result.
        """
        
        if not ax:
            fig,ax=plt.subplots(figsize=(10,10/self.ndays))
        rgb3d = self.generate_image()
        ax.imshow(rgb3d,aspect='auto')
        ax.axis('off')
        
        return ax

    def __repr__(self):
        ax = self.plot()
        plt.show()
        return ''
    
    
class WeekCalendar(DayCalendar):
    """ 
    Create a (7xn) grid with all the dates in the given range
    """
    
    def __init__(self,start_date,end_date,firstweekday=0):
        """ 
        Parameters
        ----------
        start : datetime.date
            The first day in the calendar.
        finish : datetime.date
            The last day in the calendar.
        firstweekday : int
            From 0 (Monday) to 6 (Sunday). 
        """
                
        self.start_date = to_date(start_date)
        self.end_date = to_date(end_date)
        self.firstweekday = firstweekday

        
        ndays = (end_date-start_date).days + 1

        # offset in the first column 
        # this happens when first_day.weekday() differs from firstweekday
        offset  = (start_date.weekday()-firstweekday)%7
        remnant = (7-(ndays+offset))%7
        
        dates = [start_date+datetime.timedelta(days)  for days in range(ndays)] 
        # a 2d array for the dates within the range
        self.dates = np.array((offset*[np.nan]+dates+remnant*[np.nan])).reshape(7,-1,order='F')
        # a 2d array with the months based on the previous array
        self.months = np.array((offset*[-1]+[date.month for date in dates]+remnant*[-1])).reshape(7,-1,order='F')
        self.events = dict()
        self.colors = dict()

        self.contours = find_contours(self.months,labels=np.arange(1,13))

    def plot(self,ax=None,weekday_ticks=True,grid=False):
        """ 
        This is just a simple example to showcase the grid
        """
        
        if not ax:
            fig,ax=plt.subplots(figsize=np.array(self.dates.shape)[::-1] * 0.2)
            fig.patch.set_facecolor('#ececec')
            ax.patch.set_facecolor('#ececec')
 
        rgb3d = self.generate_image()
        ax.imshow(rgb3d,zorder=1)

       
        for x,y in self.contours:
            ax.plot(x,y,color='gray',linewidth=1,zorder=2,clip_on=False)
        
        # remove xticks and set yticks to weekdays
        ax.set_xticks([])
        if weekday_ticks:
            weekdays = np.roll([datetime.date(1900,1,day).strftime('%a') for day in range(1,8)],7-self.firstweekday)
            ax.set_yticks(np.arange(0,7),weekdays)
        else:
            ax.set_yticks([])
        ax.tick_params(axis='both', which='both', length=0)
        ax.spines[["top","bottom","left","right"]].set_visible(False)
        
        if grid:
            ax.set_xticks(np.arange(self.dates.shape[1])-0.5, minor=True)
            ax.set_yticks(np.arange(7)-0.5, minor=True)
            ax.grid(which='minor', color='#ececec', linestyle='-', linewidth=1)
        
        return fig,ax 
    
    
class MonthCalendar(DayCalendar):
    
    def __init__(self,year,month,firstweekday=0):
        """  
        Create a grid with all days of the given month
        
        Parameters
        ----------
        year : int
            The year of the month.
        month : int
            The number of the month.
        firstweekday : int
            From 0 (Monday) to 6 (Sunday).
        """
        
        self.year = year
        self.month = month
        self.firstweekday = firstweekday
        
        # from those values we compute the standard values
        self.start_date  = datetime.date(year,month,1)
        self.end_date = last_day_of_month(self.start_date)
        self.ndays = (self.end_date-self.start_date).days + 1

        # the dates array is more complex due to offsets at the start end end
        offset  = (self.start_date.weekday()-firstweekday)%7
        dates = [self.start_date+datetime.timedelta(days)  for days in range(self.ndays)] 
        self.dates = np.array((offset*[np.nan]+dates+(42-offset-len(dates))*[np.nan])).reshape(6,7)

        self.events = dict()
        self.colors = dict()
        
    def add_event(self,date,event=0,format=r'%Y-%m-%d'): 
        # since we know the year and month we can also accept the day as date   
        if isinstance(date,int):
            super().add_event(datetime.date(self.year,self.month,date),event)
        else:
            super().add_event(date,event,format)
    
    def plot(self,ax=None):
        """ 
        Plot the calendar. In order to show the added events, one has to
        run self.update_colors() beforehand.
        """
        
        fontdict_month = {'fontsize':10,'color':'black','weight':'bold','va':'center','ha':'center'}
        fontdict_weekday = {'fontsize':8,'color':'black','weight':'bold','va':'center','ha':'center'}
        fontdict_day = {'fontsize':8,'color':'black','va':'center','ha':'center'}
        
        if not ax:
            fig,ax=plt.subplots(figsize=(4,4))
        
        # write day in calendar
        for date in self.dates.flat:
            if isinstance(date,datetime.date):
                col = (date.weekday()-self.firstweekday)%7
                row = (date.day + (self.start_date.weekday()-self.firstweekday)%7 -1)//7
                ax.text(col,row,f'{date.day:2d}',zorder=5,**fontdict_day)
        
        # we use January 1, 1900 as a reference. It was a Monday.
        weekdays = np.roll([datetime.date(1900,1,day).strftime('%a') for day in range(1,8)],7-self.firstweekday)
        # caption for the weekdays
        for i, weekday in enumerate(weekdays):
            ax.text(i,-1,weekday,zorder=5,**fontdict_weekday)
        # caption for the Month
        ax.text(3.,-2.25,f"{self.start_date.strftime('%B')} {self.year}",zorder=5,**fontdict_month)

        # color the dates form self.events
        rgb3d = self.generate_image()
        ax.imshow(rgb3d)

        ax.set(xlim=[-0.5,6.5],ylim=[5.5,-3])
        ax.axis('off')
    	
        return ax 
    

class YearCalendar:
    """Combine all 12 MonthGrids for one year in a nice figure"""
    
    def __init__(self,year,firstweekday=0,ncols=4):
        """     
        Parameters
        ----------
        year : int 
            The year that is used
        firstweekday : int
            From 0 (Monday) to 6 (Sunday).
        ncols : int
            Number of columns (can be 1,2,3,4,6 or 12).
        """
        
        self.year = year 
        self.firstweekday = firstweekday
        self.ncols = ncols
        self.nrows = int(12/ncols)
        
        # a dict with MonthGrid objects for each month
        self.months = {month:MonthCalendar(year,month,firstweekday) for month in range(1,13)}

    def add_event(self,date,event=1,format=r'%Y-%m-%d'):    
        """
        Pass the date and value to the correct month
        
        Add value to the events array at the given date.This method 
        overwrites existing values.
        
        Parameters
        ----------
        date : datetime.date | tuple | list
            The tuple/list (month,day) is passed to date(*tuple).
        event : object 
            Stored in self.events.
        format : str
            The format if the date is passed as a string.
        """
        
        # the case of a tuple/list we add the year and pass to datetime.date
        if isinstance(date,(tuple,list)):
            if len(date)==2:
                date = (self.year,)+tuple(date)
            date = datetime.date(*date)
            
        # add the event to the corresponding month
        self.months[date.month].add_event(date,event,format=format)

    def update_colors(self,color_dict=None,cmap='Wistia'):
        """ 
        Update the colors dictionary based on the events dictionary. 
        This method applies this method to all entries in self.months.
        """
        for month_nr, month in self.months.items():
            month.update_colors(color_dict=color_dict,cmap=cmap)

    def plot(self,grid=False,axis_size=2.36):

        fontdict_year = {'weight':'bold','color':'#1e5d3f'}
        fontdict_month = {'fontsize':10,'color':'white','weight':'bold','va':'center','ha':'center'}
        fontdict_weekday = {'fontsize':8,'color':'white','weight':'bold','va':'center','ha':'center'}
        fontdict_day = {'fontsize':8,'color':'black','va':'center','ha':'center'}
            
        # for one month the default is 6cm = 2.36in. Since we are using
        # imshow, we need to already consider the limits here
        width  = axis_size*self.ncols 
        height = axis_size*self.nrows #* 1.214
        
        fig, axes = plt.subplots(figsize=(width,height),
                                 ncols=self.ncols,nrows=self.nrows)
        fig.patch.set_facecolor('#ececec')
        
        for month_nr, month in self.months.items():
            # select the corresponding axes
            #ax = axes[(month-1)//self.ncols,(month-1)%self.ncols]
            ax = axes.flat[month_nr-1]
            
            # write day in calendar
            for date in month.dates.flat:
                if isinstance(date,datetime.date):
                    col = (date.weekday()-month.firstweekday)%7
                    row = (date.day + (month.start_date.weekday()-month.firstweekday)%7 -1)//7
                    ax.text(col,row,f'{date.day:2d}',zorder=5,**fontdict_day)
            
            # we use January 1, 1900 as a reference. It was a Monday.
            weekdays = np.roll([datetime.date(1900,1,day).strftime('%a') for day in range(1,8)],7-self.firstweekday)
            # caption for the weekdays
            for i, weekday in enumerate(weekdays):
                ax.text(i,-1,weekday,zorder=5,**fontdict_weekday)
            # caption for the Month
            ax.text(3.,-2.25,f"{month.start_date.strftime('%B')} {self.year}",zorder=5,**fontdict_month)
            
            # color the dates form self.events
            rgb3d = month.generate_image()
            ax.imshow(rgb3d,zorder=2,aspect='auto')
            
            # white background for calendar
            ax.add_patch(mpl.patches.Rectangle((-0.5,-0.5),7.5,5,color='white',zorder=1))
            ax.add_patch(mpl.patches.Circle((5.5,4.5),1,edgecolor='none',facecolor='white',zorder=1))
            ax.add_patch(mpl.patches.Rectangle((-0.5,4.5),6,1,edgecolor='none',facecolor='white',zorder=1))
            
            # caption for the Month
            ax.add_patch(mpl.patches.Circle((0.5,-2.),1,edgecolor='none',facecolor='#1e5d3f',zorder=2))
            ax.add_patch(mpl.patches.Rectangle((-0.5,-2),1,0.5,edgecolor='none',facecolor='#1e5d3f',zorder=2))
            ax.add_patch(mpl.patches.Rectangle((0.5,-3),7.5,1.5,edgecolor='none',facecolor='#1e5d3f',zorder=2))

            # caption for the weekdays
            ax.add_patch(mpl.patches.Rectangle((-0.5,-1.5),7.5,1,color='#00a770',zorder=3))
            
            # we draw the grid by hand
            if grid:
                for x in range(6):
                    ax.plot([x+0.5,x+0.5],[-0.5,5.5],color='#ececec',zorder=2)
                for y in range(5):
                    ax.plot([-0.5,6.5],[y+0.5,y+0.5],color='#ececec',zorder=2)
            
            ax.set(xlim=[-0.5,6.5],ylim=[5.5,-3])
            ax.axis('off')
            
        fig.suptitle(self.year,fontsize=16,y=0.98,**fontdict_year)
        plt.tight_layout()
        
        return fig, axes
    
 
    
if __name__=='__main__':

    # to_date()
    solution = datetime.date(1900,1,1)
    for arg in [datetime.date(1900,1,1),datetime.datetime(1900,1,1,0,0),
                (1900,1,1),[1900,1,1],'1900-01-01']: 
        answer = to_date(arg)
        assert  answer == solution, f'{answer} does not equal {solution}'
        
        
    # last_day_of_month() 
    for i, len_month in enumerate([31,29,31,30,31,30,31,31,30,31,30,31]):
        last_day = last_day_of_month(2020,i+1,15)
        assert last_day.day == len_month, f'wrong number for {i+1}'
        
        
    # range_of_dates() (difficult to assert, just look at the result)
    start_date = datetime.date(1900,1,10)
    end_date = datetime.date(1900,1,20)

    # going forward
    range_of_dates(start_date=start_date,end_date=end_date) # start_date and end_date
    range_of_dates(start_date=end_date)                     # only start_date
    range_of_dates(end_date=start_date)                     # only end_date
    range_of_dates(start_date=start_date,ndays=5)           # start_date and ndays
    range_of_dates(end_date=end_date,ndays=5)               # end_date and ndays

    # other direction with negative sign
    range_of_dates(start_date=start_date,ndays=-5)          # start_date and -ndays
    range_of_dates(end_date=end_date,ndays=-5)              # end_date and -ndays
    range_of_dates(start_date=end_date,end_date=start_date) # switch start_date and end_date
            
            
    # Date()
    # we first check the input (should work if to_date works)
    solution = datetime.date(1900,1,1)
    for arg in [datetime.date(1900,1,1),datetime.datetime(1900,1,1,0,0),
                (1900,1,1),[1900,1,1],'1900-01-01']: 
        answer = Date(arg)
        assert  answer == solution, f'error for type {type(arg)}'
    # we check the summation    
    assert Date('2000-01-01')+datetime.timedelta(1) == Date('2000-01-02'), 'error when adding timedelta'
    assert Date('2000-01-01')+1 == Date('2000-01-02'), 'error when adding integer'
    # and the subtraction
    assert Date('2000-01-02')-1 == Date('2000-01-01'), 'error when subtracting integer'
    assert Date('2000-01-02')-datetime.timedelta(1) == Date('2000-01-01'), 'error when subtracting timedelta'
    assert Date('2000-01-02')-Date('2000-01-01') == datetime.timedelta(1), 'error when subtracting dates'
