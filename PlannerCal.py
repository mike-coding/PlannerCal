import tkinter as tk
import sv_ttk
from tkinter import ttk
import time
import calendar
import datetime
import functools as ft
import math
import json

# TO-DO: FIXES
#
# 1. [FIXED] Buttons flash on refresh when changing day within month -> CalendarFrame.update_selected_date()
# 2. [FIXED] Can't jump months if selected day doesnt exist in target month

# TO-D0: FEATURES
#
# 1. [IMPLEMENTED] plan logic
# 2. todolist



class AppWindow(object):

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']
    weekdays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
    app_origin = [0, 0]

    root = tk.Tk()
    root.iconbitmap(r'C:\Users\Admin\PycharmProjects\Calendar App 226\ultracalendaricon.ico')
    root.title('PlannerCal V1')
    sv_ttk.set_theme("light")

    def __init__(self):
        self.init_state()
        AppWindow.instance=self
        main_todo_frame = TodoFrame(datetime.date.today())
        main_calendar = CalendarFrame(datetime.date.today())
        AppWindow.root.mainloop()

    def save_state(self):
        preSave = dict()
        print('\n\n__save_state init__')
        print(f'Plan.plandict contents to be comitted: {Plan.plandict}')
        for key in Plan.plandict:
            strKey = self.convert_datetime_key_str(key)
            print(f'\nadding {strKey}:{Plan.plandict[key][0].get_params_in_list()} to preSave')
            preSave[strKey] = [Plan.plandict[key][0].get_params_in_list()]

            if len(Plan.plandict[key])!=1:
                for i in range(1,len(Plan.plandict[key])):
                    preSave[strKey].append(Plan.plandict[key][i].get_params_in_list())
                    print(f'    {strKey}:{Plan.plandict[key][i].get_params_in_list()} added to preSave')

        plan_save = json.dumps(preSave)
        savefile = open('savefile.json','w')
        savefile.write(plan_save)
        print(f'\ncontents written to JSON: {preSave}')
        print('__save_state complete__')

    def convert_datetime_key_str(self,datetime):
        return str(datetime)

    def convert_str_key_datetime(self,str):
        dateList=str.split('-')
        dateList = [int(x) for x in dateList]
        return datetime.date(dateList[0],dateList[1],dateList[2])

    def load_state(self):
        saveLoad = json.load(open('savefile.json','r'))
        planLoad=dict()
        print('\n\n__load_state init__')
        print(f'savefile contents to be comitted: {saveLoad}')
        for date in saveLoad:
            datetime_object = self.convert_str_key_datetime(date)
            print(f'\nloading tasks for date: {date}')
            for plan in saveLoad[date]:
                print(f'    adding plan: {plan}')
                newPlan = Plan(plan[0], datetime_object)
                newPlan.date = datetime_object
                newPlan.category = plan[1]
                newPlan.isSeries = plan[2]
                newPlan.seriesFreq = plan[3]
                newPlan.isComplete = plan[4]

                if datetime_object in planLoad:
                    planLoad[datetime_object].append(newPlan)
                else:
                    planLoad[datetime_object] = [newPlan]

        Plan.plandict = planLoad
        print(f'\ncontents written to Plan.plandict: {Plan.plandict}')
        print('__load_state complete__\n')

    def init_state(self):
        try:
            self.load_state()
        except FileNotFoundError:
            self.save_state()





class TodoFrame(object):
    _reg=list()
    def __init__(self,date):
        self.state = 'UPCOMING'
        self.fcn = lambda: 'Accent.TButton' if self.state == 'UPCOMING' else None
        self.selected_date = date
        self.draw_buttons()
        self.draw_todolist()
        TodoFrame._reg.append(self)


    def draw_buttons(self):
        self.date_button = ttk.Button(AppWindow.root,
                                      text='XX/XX/XXXX',
                                      style=self.return_button_style(self.selected_date),
                                      command=ft.partial(self.update_state,self.selected_date))
        self.date_button.grid(row=AppWindow.app_origin[1],
                              column=AppWindow.app_origin[0]+1,
                              pady=(10,8))
        self.upcoming_button = ttk.Button(AppWindow.root,
                                          text='UPCOMING',
                                          style=self.return_button_style('UPCOMING'),
                                          command=ft.partial(self.update_state,'UPCOMING'))
        self.upcoming_button.grid(row=AppWindow.app_origin[1],
                                  column=AppWindow.app_origin[0],
                                  pady=(10,8))

        ttk.Button(AppWindow.root,text='«')\
            .grid(row=AppWindow.app_origin[1]+2,
                  column=AppWindow.app_origin[0],
                  sticky='e',padx=(0,30),
                  pady=(10,10))
        ttk.Button(AppWindow.root, text='»') \
            .grid(row=AppWindow.app_origin[1] + 2, column=AppWindow.app_origin[0]+1, sticky='w',padx=(30,0),pady=(10,10))

    def draw_todolist(self):
        self.frame = ttk.LabelFrame(AppWindow.root,text='TO-DO', width=240, height=100)
        self.frame.grid(padx=(10,10),row=AppWindow.app_origin[1]+1,column=AppWindow.app_origin[0],columnspan=2,sticky='n')
        self.populate_todolist()

    def return_button_style(self,state):
        if self.state == state:
            return 'Accent.TButton'
        else:
            return 'TButton'

    def populate_todolist(self):
        self.currentTaskEntries=list()
        # draw entry field
        self.newtask_button=ttk.Button(self.frame,text='+',style='Accent.TButton',command=self.add_new_plan)
        self.newtask_button.grid(row=0,column=0,padx=(10,4),pady=(5,5))
        self.newtask_entry=ttk.Entry(self.frame)
        self.newtask_entry.grid(row=0,column=1,padx=(4,4))
        self.newtask_settings = ttk.Button(self.frame,text='...')
        self.newtask_settings.grid(row=0,column=2,padx=(4,10))
        # check state
        if self.state == 'UPCOMING':
            print(f'[UPCOMING PLANS]:')
            for plan in enumerate(Plan.get_upcoming_plan_list()):
                if plan[0] < 9:
                    self.draw_todo_entry(plan[0],plan[1])
                    print(f'{plan[0]}:{plan[1].title}')

        # if datemode:
        try:
            for plan in enumerate(Plan.plandict[self.selected_date]):
                self.draw_todo_entry(plan[0],plan[1])
        except KeyError:
            pass

    def draw_todo_entry(self,pos,plan):
        entry_components = list()
        toggle_plan = lambda x: x.toggle_completion_status()
        entry_components.append(ttk.Checkbutton(self.frame,command=ft.partial(toggle_plan,plan)))
        entry_components[-1].grid(row=pos+1,column=0,padx=(12,6),pady=(5,5))
        entry_components.append(ttk.Label(self.frame,text=plan.title))
        entry_components[-1].grid(row=pos + 1, column=1,sticky='w', padx=(6,6))

        pass

    def add_new_plan(self):
        title= str(self.newtask_entry.get()).strip()
        if title!='':
            Plan(title,self.selected_date)
        AppWindow.instance.save_state()
        #print(Plan.plandict[self.selected_date])

    def set_selected_date(self,date):
        if date==None:
            self.selected_date=datetime.date.today()
        else:
            self.selected_date=CalendarFrame._reg[0].selected_date[0]

        if self.selected_date!=CalendarFrame._reg[0].selected_date[0]:
            CalendarFrame._reg[0].update_selected_date(day=self.selected_date.day, month=self.selected_date.month,
                                                   year=self.selected_date.year)

        self.update_todolist()

    def update_todolist(self):
        self.clear_todolist()
        self.populate_todolist()

    def clear_todolist(self):
        pass

    def check_date_against(self, date, object_of_date, index):
        # this doesn't do anything right now, but maybe it'll be useful somehow
        index_dict={0:(date.day,object_of_date.selected_date[0].day),
                    1:(date.month,object_of_date.selected_date[0].month),
                    2:(date.year,object_of_date.selected_date[0].year)}
        if index_dict[index][0] != index_dict[index][1]:
            pass

    def update_state(self,date):
        if date=='UPCOMING':
            self.set_selected_date(None)
            self.upcoming_button.config(style='Accent.TButton')
            self.date_button.config(style='TButton')
        else:
            self.set_selected_date(date)
            self.upcoming_button.config(style='TButton')
            self.date_button.config(style='Accent.TButton')
        self.state = date





class CalendarFrame(object):
    _reg=list()
    def __init__(self,date):
        self.selected_date=self.calculate_selected_date_data(date)
        self.draw_buttons()
        self.draw_calendar()
        CalendarFrame._reg.append(self)


    def draw_buttons(self):
        ttk.Button(AppWindow.root, text='«', command=ft.partial(self.jump_month, -1)) \
            .grid(row=AppWindow.app_origin[1], column=AppWindow.app_origin[0]+2, sticky='e', padx=(0, 30),
                  pady=(10, 10))
        ttk.Button(AppWindow.root, text='»', command=ft.partial(self.jump_month, 1)) \
            .grid(row=AppWindow.app_origin[1], column=AppWindow.app_origin[0]+4, sticky='w', padx=(30, 0),
                  pady=(10, 10))

    def draw_calendar(self):
        self.frame = ttk.Frame(AppWindow.root, width=500, height=300,style='Card.TFrame')
        self.frame.grid(padx=(10, 10), row=AppWindow.app_origin[1] + 1, column=AppWindow.app_origin[0]+2, columnspan=3,
                        sticky='n',pady=(8.5,0))

        self.draw_weekday_labels()
        self.populate_calendar()

    def draw_weekday_labels(self):
        for i in range(len(AppWindow.weekdays)):
            ttk.Label(self.frame,text=AppWindow.weekdays[i]).grid(row=0,column=i,padx=(25,25),pady=(5,10),sticky='nesw')

    def calculate_selected_date_data(self, date):
        column_calc = lambda x: x + 1 if x != 6 else 0
        monthrange_data=calendar.monthrange(date.year,date.month)
        first_weekday_in_month=column_calc(monthrange_data[0])
        days_in_month=monthrange_data[1]
        maxrow= math.ceil((days_in_month + first_weekday_in_month)/7)
        return (date,days_in_month,first_weekday_in_month,maxrow)

    def populate_calendar(self):
        # Month/Year label
        self.label = ttk.Label(AppWindow.root, text=str(AppWindow.months[self.selected_date[0].month - 1])+' '+
                                                    str(self.selected_date[0].year))
        self.label.grid(row=AppWindow.app_origin[1], column=AppWindow.app_origin[0] + 3)

        # find a better home for this
        day_bg= lambda x: '#CCD6E0' if x==self.selected_date[0].day else None

        # generates day buttons
        _column=self.selected_date[2]
        _row=1
        for i in range(1,self.selected_date[1]+1):
            tk.Button(self.frame,text=i,relief='flat',height=4,width=10,anchor='nw',borderwidth=0,bg=day_bg(i),
                      command=ft.partial(self.update_selected_date,day=i))\
                .grid(row=_row,column=_column,padx=self.calendar_padding_calculator(_column,'x'),
                      pady=self.calendar_padding_calculator(_row,'y'),sticky='n')

            # spatial handling on grid
            _column+=1
            if (i-(7-self.selected_date[2]))%7==0:
                _row+=1
                _column=0

        self.update_day_button_list()

    def update_day_button_list(self):
        self.buttons = [button for button in self.frame.winfo_children() if 'button' in str(button)]

    def clear_calendar(self):
        for button in self.buttons:
            button.destroy()
        self.buttons=[]

        self.label.destroy()

    def refresh_calendar(self):
        self.clear_calendar()
        self.populate_calendar()

    def select_day(self,_day):
        self.buttons[self.selected_date[0].day-1].config(bg='#FAFAFA')
        self.buttons[_day - 1].config(bg='#CCD6E0')

    def jump_month(self,direction):
        year_update = self.selected_date[0].year

        if direction<0:
            month_update = self.selected_date[0].month - 1

        elif direction>0:
            month_update = self.selected_date[0].month + 1

        if month_update>12:
            month_update=1
            year_update+=1
        if month_update<1:
            month_update=12
            year_update-=1
        try:
            self.update_selected_date(month=month_update,year=year_update)

        except ValueError:
            self.update_selected_date(month=month_update, year=year_update, day=1)

    def update_selected_date(self,**kwargs):
        update_cal=False
        update_day=False
        oldday=self.selected_date[0].day
        newday=self.selected_date[0].day
        newmonth=self.selected_date[0].month
        newyear=self.selected_date[0].year

        if 'day' in kwargs and kwargs['day'] !=newday:
            newday = kwargs['day']
            self.select_day(newday)
        if 'month' in kwargs and kwargs['month'] !=newmonth:
            newmonth=kwargs['month']
            update_cal=True
        if 'year' in kwargs and kwargs['year'] !=newyear:
            newyear=kwargs['year']
            update_cal=True

        self.selected_date= self.calculate_selected_date_data(datetime.date(year=newyear,month=newmonth,day=newday))
        TodoFrame._reg[0].set_selected_date(self.selected_date[0])

        if update_cal:
            self.refresh_calendar()

    def calendar_padding_calculator(self,columnrow,axis):
        if axis == 'x':
            if columnrow==0:
                return (10,0)
            elif columnrow ==6:
                return (0,10)
            else:
                return(0,0)
        elif axis == 'y':
            if columnrow == self.selected_date[3]:
                return (0,10)
            elif columnrow==1:
                return (15,0)
            else:
                return (0,0)




class Plan(object):
    plandict=dict()

    def get_upcoming_plan_list():
        flat_upcoming = list()
        for key in Plan.plandict:
            for plan in Plan.plandict[key]:
                if not plan.isComplete:
                    flat_upcoming.append(plan)
        getDate = lambda x: x.date
        flat_upcoming = sorted(flat_upcoming,key=getDate)
        return flat_upcoming

    def __init__(self,title,date):
        self.date = date
        self.title = title
        self.category = None
        self.isSeries = False
        self.seriesFreq = None # 0 = daily, 1 = weekly, 2 = monthly, 3 = yearly
        self.isComplete = False

        # print(f'plan {self.title} created for date: {date}')
        self.add_to_plandict()

    def add_to_plandict(self):
        if self.date not in Plan.plandict:
            Plan.plandict[self.date]=[self]
        else:
            Plan.plandict[self.date].append(self)

    def get_params_in_list(self):
        return [self.title,self.category,self.isSeries,self.seriesFreq,self.isComplete]

    def toggle_completion_status(self):
        if not self.isComplete:
            self.isComplete = True
        elif self.isComplete:
            self.isComplete = False





main = AppWindow()
