# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T16:29:16.583956Z","iopub.execute_input":"2023-12-09T16:29:16.584462Z","iopub.status.idle":"2023-12-09T16:29:35.775266Z","shell.execute_reply.started":"2023-12-09T16:29:16.584423Z","shell.execute_reply":"2023-12-09T16:29:35.774073Z"}}
# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python Docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import streamlit as st



import pulp
pd.reset_option('max_columns')
import re
data=pd.read_csv('major_ptoject_normalise_data_final.csv')






# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T16:35:49.107726Z","iopub.execute_input":"2023-12-09T16:35:49.108159Z","iopub.status.idle":"2023-12-09T16:35:49.152178Z","shell.execute_reply.started":"2023-12-09T16:35:49.108123Z","shell.execute_reply":"2023-12-09T16:35:49.151054Z"}}
data=data.fillna(0)
data=data[0:409]
data = data.rename(columns=lambda x: x.strip())
data



# %% [code]


# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T16:09:40.074241Z","iopub.execute_input":"2023-12-09T16:09:40.074715Z","iopub.status.idle":"2023-12-09T16:09:40.106821Z","shell.execute_reply.started":"2023-12-09T16:09:40.074672Z","shell.execute_reply":"2023-12-09T16:09:40.105733Z"}}
def lpmodel2(team,excData):
    
    prob = pulp.LpProblem('Dreamteam', pulp.LpMaximize)
    nC=excData.shape[1]
    
  #################normalize
    for i in range(14,nC):
        if(type(excData.iloc[:,i][0])==str):
            continue
        excData.iloc[:,i]=excData.iloc[:,i]/excData.iloc[:,i].max()
  ####################
   ##############################decision variable     
    decision_variables = []

    for rownum, row in excData.iterrows():
        
        variable = str('x_{}'.format(str(rownum)))
        variable = pulp.LpVariable(variable, lowBound = 0, upBound = 1, cat = 'Integer' ) 
        decision_variables.append(variable)
   #########################################
    total_points = ''

    overallPf=[]
    ###############################price
 
    
    #####################################

    nC=excData.shape[1]

    excData['overall']=0
    for i in range(14,nC):
        if(type(excData.iloc[:,i][0])==str):
            continue
        excData['overall']+=excData.iloc[:,i]*1
    ##############3
    for p in team.players:
        excData['overall'][p]=-1
    ###############3
    total_points = ''
    for rownum, row in excData.iterrows():
        
        formula = row['overall'] * decision_variables[rownum]
        total_points+= formula
   # prob += total_points
    total_players=0
##########################################
    for rownum, row in excData.iterrows():
       
        total_players_formula = decision_variables[rownum]
        total_players += total_players_formula
    prob+=(total_players==team.maxTeamSize-len(team.retained_players))
##########################################

            
  
 #######################
################conditions start
#bad batsman
  #  bad_batsman_count=''
   # for rownum, row in excData.iterrows():
       
   #     if row['overall']>20 and row['overall']<25:
    #        bad_batsman_count+=decision_variables[rownum]
    #prob+=(bad_batsman_count>=4)
    
    conditions=team.conditions
    
    abc=''
    efg=''
    for key in conditions:
        columnsBin=conditions[key][0]
        valueBin=conditions[key][1]
        columns=conditions[key][2]
        weightage=conditions[key][3]
        req=max(0,conditions[key][4])
        #reqtype=conditions[key][3]
        sz=len(columns)
        name=key+"solve"
        excData[name]=0
        for idx,c in enumerate(columns):
            excData[name]+=excData.iloc[:,c]*weightage[idx]


        for rownum,row in excData.iterrows():
                flag=True
                for inx,cl in enumerate(columnsBin):
                    if(excData[cl][rownum]!=valueBin[inx]):
                        flag=False
                if flag:
                    abc+=excData[name][rownum]*decision_variables[rownum]
                    efg+=1*decision_variables[rownum]
                else:
                    abc+=0*excData[name][rownum]*decision_variables[rownum]
                    efg+=0*decision_variables[rownum]
                
         
        prob+=(efg>=req)
        #abc=''
        efg=''
    prob+=(abc)  
                
                
                
      #  prob+=(efg>=req[0])
      #  prob+=(efg<=req[0]+1)
       #  if len(req)>1:
        #    prob+=(efg<=req[1])
            
     
        
        
####################conditions end
########################################
    price=''
    
    for rownum,row in excData.iterrows():
        price+=decision_variables[rownum]*excData['base_price_in_lakhs'][rownum]
    prob+=(price<=(0.48*team.fund-200))
        

#######################################
    ########retained remover
    retained=''
    
    for rownum,row in excData.iterrows():
        retained+=decision_variables[rownum]*excData['retained_players'][rownum]
    prob+=(retained==0)
    
 ##################################################
#######################################
    ########retired remover
    retired=''
    
    for rownum,row in excData.iterrows():
        retired+=decision_variables[rownum]*excData['retired_player'][rownum]
    prob+=(retired==0)
    
 ##################################################
#######################################
    ########overseas condition
    overseas=''
    
    for rownum,row in excData.iterrows():
        overseas+=decision_variables[rownum]*excData['overseas'][rownum]
    prob+=(overseas<=team.maxOverseasLeft)
    
 ##################################################
    #print(prob)
    prob.writeLP('Dreamteam.lp')
    
    try:
       optimization_result = prob.solve()
       team.lpSuccess=True
    except Exception as e:
        print("Failure")
        team.lpSuccess=False
        result=excData.drop(excData.index)
        return result


    print("done")
    variable_name = []
    variable_value = []

    for v in prob.variables():
        variable_name.append(v.name)
        variable_value.append(v.varValue)
    df = pd.DataFrame({'index': variable_name, 'value': variable_value})
    for rownum, row in df.iterrows():
        value = re.findall(r'(\d+)', row['index'])
        df.loc[rownum, 'index'] = int(value[0])
    df = df.sort_values(by = 'index')
    excData['index'] = excData.index

    result = pd.merge(excData, df,on = 'index')

    result = result[result['value'] == 1].sort_values(by = 'overall', ascending = False)
    result.to_csv("resultt.csv", index=True)
    
    ###maxPrice###

    return result
    


    

# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T16:09:41.855382Z","iopub.execute_input":"2023-12-09T16:09:41.856397Z","iopub.status.idle":"2023-12-09T16:09:41.891519Z","shell.execute_reply.started":"2023-12-09T16:09:41.856358Z","shell.execute_reply":"2023-12-09T16:09:41.890049Z"}}
diverse=['pure_batter','pure_medium_pacer','pure_spinner','wicket_keeper','all_rounder','overseas']

def clc(t,data):
    players=t.players
    squad=t.squad
    for p in players:
        if data['batsman'][p] and  not data['is_wicket_keeper'][p]:
            t.squad['pure_batter'].append(p)
            print(p)
        if data['batsman'][p] and data['is_wicket_keeper'][p]:
            t.squad['wicket_keeper'].append(p)
        if data['bowler'][p] and data['spinner_or_medium_pacer'][p]=='M':
            t.squad['pure_medium_pacer'].append(p)
        if data['bowler'][p] and data['spinner_or_medium_pacer'][p]=='S':
            t.squad['pure_spinner'].append(p)
        if data['all_rounder'][p]:
            t.squad['all_rounder'].append(p)
        if data['overseas'][p]:
            t.squad['overseas'].append(p)
    print(t.squad)    
    return t.squad
            
    


roles=[0,1,2,3,4,5]
#roles 0-opener batsman
#roles 1-middle batsman
#roles 3-lower bastamn
#roles 4-batting all rounder
#roles 5-bowling all rounder
#roles 6-Medium pacer
#roles 7-Spinner
#roles 8-Wicket Keeper
class Team:
  def __init__(self, name):
    self.name = name
    self.maxTeamSize=22
    self.players=[]
    self.retained_players=[]
    self.playersToBid=[]
    self.playersToBidDf=pd.DataFrame()

    self.lpSuccess=True
    self.roleCount={}
    self.conditions={}
    for r in roles:
        self.roleCount[r]=0
    self.fund=10000
    self.maxOverseasLeft=10
       
    for rownum,row in data.iterrows():
        if self.name==data['retained_team'][rownum]:
            self.retained_players.append(rownum)
            self.fund-=data['sold_price'][rownum]
            self.players.append(rownum)
    
    self.squad={}
    for d in diverse:
        self.squad[d]=[]
    self.squad=clc(self,data)
    
    
            
            
  def set_maxTeamSize(self,a): 
    self.maxTeamSize=a
    return self.maxTeamSize 
       
  def get_maxTeamSize(self): 
    return self.maxTeamSize
  

#  def addPlayer(self,player_id,role,price):
#    self.players.append(player_id)
  #  self.roleCount[role]+=1
 #   self.fund-=price
#    return player_id
    
  def runLP(self,data,aucExc):
    exclude_data=data
    if(aucExc!=-1):
        exclude_data=data.iloc[aucExc:]
        exclude_data=exclude_data.reset_index(drop=True)
    ap= lpmodel2(self,exclude_data)


    ap['maxPrice']=0
    for rownum,row in ap.iterrows():
        for key in self.conditions:
            ap['maxPrice'][rownum]=max(ap['maxPrice'][rownum],ap[key+"solve"][rownum])
    ap['maxPrice']=ap['maxPrice']*ap['sold_price']
    current_sum = ap['maxPrice'].sum()

# Normalize prices
    ap['maxPrice'] = ap['maxPrice'] * ((self.fund-500) / current_sum) if current_sum > 0 else 0
    for rownum,row in ap.iterrows():
        ap['maxPrice'][rownum]=max(ap['maxPrice'][rownum],ap['base_price_in_lakhs'][rownum]+10)


    
        
    ap.to_csv("res")
    

    
    return ap

  def adder(self,player_id,price): 
    self.players.append(player_id)
    self.fund-=price
    self.squad={}
    for d in diverse:
        self.squad[d]=[]
    self.squad=clc(self,data)
    return self.fund
 
  def remover(self,player_id,price):
    self.players.remove(player_id)
    self.fund+=price
    return self.fund
  
  def setConditions(self,name,columnsBin,valueBin,columns,weightage,req):
    self.conditions[name]=[[],[],[],[],[]]
    self.conditions[name][0]=columnsBin
    self.conditions[name][1]=valueBin
    self.conditions[name][2]=columns
    self.conditions[name][3]=weightage
    self.conditions[name][4]=req
    return self.fund

  def removeConditions(self,name):
        del self.conditions[name]
        return self.fund
    
  def checker(self,player,currentPrice):
    rownum=player-1
    if rownum in self.playersToBid:
        if currentPrice<=self.playersToBidDf['maxPrice'][rownum]:
            return True
    return False
        
    
    
    
  
    
def mainFunc(name,maxTeamSize,diverseList,aucExc,bought):
    t=Team(name)
    t.maxTeamSize=maxTeamSize
    t.maxOverseasLeft=diverseList[5]-len(t.squad[diverse[5]])

    #################################################################
    team_batting_mapping = {
    "DC": 61, "RCB": 63, "KKR": 65, "CSK": 67, "GT": 69,
    "PK": 71, "MI": 73, "LSG": 75, "RR": 77, "SRH": 79
    }     
    pure_batter_columns=[15, 16, 18, 19, 21, 22, 24, 32, 33, 34, 35, 36]
    pure_batter_columns.append(team_batting_mapping[name])
    pure_batter_weightage=[1 for i in range(len(pure_batter_columns))]
    pure_batter_weightage[-1]=50
    ################################################################
    team_bowling_mapping = {
    "DC": 62, "RCB": 64, "KKR": 66, "CSK": 68, "GT": 70,
    "PK": 72, "MI": 74, "LSG": 76, "RR": 78, "SRH": 80
     }    
    pure_bowling_columns=[38,42,44,46,47,50,52,53,56,58,59]
    pure_bowling_columns.append(team_bowling_mapping[name])
    pure_bowling_weightage=[1 for i in range(len(pure_bowling_columns))]
    pure_bowling_weightage[-1]=50

    ################################################################
    all_rounder_columns=pure_batter_columns+pure_bowling_columns
    all_rounder_weightage=pure_batter_weightage+pure_bowling_weightage
    ##############################################################

    t.setConditions("pure_batter",["batsman",'retained_players','retired_player'],[1,0,0],pure_batter_columns,pure_batter_weightage,diverseList[0]-len(t.squad[diverse[0]]))
    t.setConditions("pure_medium_pacer",["bowler",'spinner_or_medium_pacer','retained_players','retired_player'],[1,'M',0,0],pure_bowling_columns,pure_bowling_weightage,diverseList[1]-len(t.squad[diverse[1]]))

    t.setConditions("pure_spinner",["bowler",'spinner_or_medium_pacer','retained_players','retired_player'],[1,'S',0,0],pure_bowling_columns,pure_bowling_weightage,diverseList[2]-len(t.squad[diverse[2]]))

    t.setConditions("wicket_keeper",["is_wicket_keeper",'retained_players','retired_player'],[1,0,0],pure_batter_columns,pure_batter_weightage,diverseList[3]-len(t.squad[diverse[3]]))
    t.setConditions("all_rounder",["all_rounder",'bowler','retained_players','retired_player'],[1,0,0,0],all_rounder_columns,all_rounder_weightage,diverseList[4]-len(t.squad[diverse[4]]))
    
    for key,value in bought.items():
        t.adder(key,value)
    t.playersToBidDf=t.runLP(data,aucExc)
    for rownum,row in t.playersToBidDf.iterrows():
        t.playersToBid.append(rownum)

 
        
    


    return t

    
    
    
    

        
       
       
    
    
    
 
    
    
    
          
    
    

# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T16:09:43.818806Z","iopub.execute_input":"2023-12-09T16:09:43.819903Z","iopub.status.idle":"2023-12-09T16:09:44.748355Z","shell.execute_reply.started":"2023-12-09T16:09:43.819866Z","shell.execute_reply":"2023-12-09T16:09:44.747279Z"}}
t=mainFunc("PK",25,[5,5,2,2,5,10],-1,{})


# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T16:09:45.381723Z","iopub.execute_input":"2023-12-09T16:09:45.382148Z","iopub.status.idle":"2023-12-09T16:09:45.388313Z","shell.execute_reply.started":"2023-12-09T16:09:45.382114Z","shell.execute_reply":"2023-12-09T16:09:45.387587Z"}}
t.playersToBid

# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T16:09:46.556694Z","iopub.execute_input":"2023-12-09T16:09:46.557941Z","iopub.status.idle":"2023-12-09T16:09:46.590447Z","shell.execute_reply.started":"2023-12-09T16:09:46.557887Z","shell.execute_reply":"2023-12-09T16:09:46.588910Z"}}
t.playersToBidDf


# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T13:40:17.691551Z","iopub.execute_input":"2023-12-09T13:40:17.691946Z","iopub.status.idle":"2023-12-09T13:40:17.698059Z","shell.execute_reply.started":"2023-12-09T13:40:17.691913Z","shell.execute_reply":"2023-12-09T13:40:17.697164Z"}}
t.checker(125,55) #auction for sandeep sharma and current bid price is 90



# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T10:46:29.470527Z","iopub.execute_input":"2023-12-09T10:46:29.470920Z","iopub.status.idle":"2023-12-09T10:46:29.479567Z","shell.execute_reply.started":"2023-12-09T10:46:29.470889Z","shell.execute_reply":"2023-12-09T10:46:29.478042Z"}}
t.checker(297,96) #auction for sandeep sharma and current bid price is 96


# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T09:28:43.307813Z","iopub.execute_input":"2023-12-09T09:28:43.308225Z","iopub.status.idle":"2023-12-09T09:28:43.316018Z","shell.execute_reply.started":"2023-12-09T09:28:43.308192Z","shell.execute_reply":"2023-12-09T09:28:43.315157Z"}}

#t.setConditions("cond2",["batsman","bowler","batting_hand",'retained_players'],[1,0,0,0],[16],[1],[4])
#t.setConditions("cond3",["all_rounder",'bowler','overseas','retained_players'],[1,0,1,0],[16,39],[0.5,0.5],[6])
#t.setConditions("cond4",["is_wicket_keeper",'retained_players'],[1,0],[16],[1],[3])

#t.setConditions("cond5",["batsman","bowler",'spinner_or_medium_pacer','bowling_hand','retained_players'],[0,1,'M',0,0],[39],[1],[4,5])
#t.setConditions("cond6",["batsman","bowler",'spinner_or_medium_pacer','bowling_hand','retained_players'],[0,1,'M',1,0],[39],[1],[4,5])
#t.setConditions("cond1",["batsman","bowler",'retained_players'],[1,0,0],[16,68],[0.5,0.5],[7])








#t.setConditions("bal",[78],[1],[0,5])

t.squad

# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T13:40:40.938429Z","iopub.execute_input":"2023-12-09T13:40:40.938808Z","iopub.status.idle":"2023-12-09T13:40:40.949198Z","shell.execute_reply.started":"2023-12-09T13:40:40.938776Z","shell.execute_reply":"2023-12-09T13:40:40.947433Z"}}
t.adder(155,51)


# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T13:40:49.233770Z","iopub.execute_input":"2023-12-09T13:40:49.234153Z","iopub.status.idle":"2023-12-09T13:40:49.240968Z","shell.execute_reply.started":"2023-12-09T13:40:49.234120Z","shell.execute_reply":"2023-12-09T13:40:49.240123Z"}}
t.players

# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T13:40:55.255788Z","iopub.execute_input":"2023-12-09T13:40:55.256344Z","iopub.status.idle":"2023-12-09T13:40:55.262299Z","shell.execute_reply.started":"2023-12-09T13:40:55.256312Z","shell.execute_reply":"2023-12-09T13:40:55.261405Z"}}
t.squad

# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T05:11:31.216449Z","iopub.execute_input":"2023-12-09T05:11:31.217091Z","iopub.status.idle":"2023-12-09T05:11:31.223888Z","shell.execute_reply.started":"2023-12-09T05:11:31.217053Z","shell.execute_reply":"2023-12-09T05:11:31.222708Z"}}


# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T05:11:32.659599Z","iopub.execute_input":"2023-12-09T05:11:32.659998Z","iopub.status.idle":"2023-12-09T05:11:32.691917Z","shell.execute_reply.started":"2023-12-09T05:11:32.659968Z","shell.execute_reply":"2023-12-09T05:11:32.690866Z"}}


# %% [code] {"execution":{"iopub.status.busy":"2023-12-09T05:11:33.588019Z","iopub.execute_input":"2023-12-09T05:11:33.588421Z","iopub.status.idle":"2023-12-09T05:11:33.595884Z","shell.execute_reply.started":"2023-12-09T05:11:33.588391Z","shell.execute_reply":"2023-12-09T05:11:33.594298Z"}}
data['overall'][285]

# %% [code]
