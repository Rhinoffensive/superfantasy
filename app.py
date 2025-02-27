from yahoo_oauth import OAuth2
import yahoo_fantasy_api as yfa
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px
import plotly.graph_objects as go

Gold_Medal = "🥇"
Silver_Medal = "🥈"
Bronze_Medal = "🥉"

st.set_page_config(layout="wide")

# Fetch user's teams
sc = OAuth2(None, None, from_file='oauth2.json')
##Fantasy League 2023-2024 ID
league_id = '428.l.17054'
image = open('logo.png', 'rb').read()
st.sidebar.image(image, caption='', width=100)

##Access token check.
if not sc.token_is_valid():
    sc.refresh_access_token()

lg = yfa.league.League(sc, league_id)
teams = yfa.league.League(sc, league_id).teams()

teams_list = {}
weeks_list = []
for team_key in teams:
    teams_list[teams[team_key]['name']] = team_key

teams_list = {team['name']: key for key, team in teams.items()}

for i in range(1, lg.current_week() + 1):
    weeks_list.append("Week " + str(i))

# Step 4: Parse and print the team names
st.sidebar.title("NBA Super Fantazi")

team_options = sorted(teams_list.keys())
team_select = st.sidebar.selectbox("Select a team",team_options)

mode_options = ["Alternate Universe", "Alternate Universe - Matchups", "Power Rankings", "Medal Board", "Box Plots", "Total Stats"]
mode_select = st.sidebar.selectbox("Select mode", mode_options)

if mode_select == "Box Plots":
    boxplot_sub_mode_options = ["Box - Weekly", "Box & SD - Weekly", "Box - Total"]
    sub_mode_select = st.sidebar.selectbox("Select submode", boxplot_sub_mode_options)
    if sub_mode_select == "Box - Weekly" or sub_mode_select == "Box & SD - Weekly":
        week_options = weeks_list
        week_select = st.sidebar.selectbox("Select a week", week_options)

if mode_select == "Alternate Universe - Matchups":
    matchup_options = sorted(teams_list.keys())
    matchup_select = st.sidebar.selectbox("Select a matchup", matchup_options)
    cross_points_df = pd.DataFrame(columns=['Week','Team_Name', 'Score', 'FG', 'FT', 'threePtm', 'Points', 'Rebound', 'Assists', 'Steal', 'Block', 'To'], index=range(2))
    cross_color_df = pd.DataFrame(columns=['Week','Team_Name', 'Score', 'FG', 'FT', 'threePtm', 'Points', 'Rebound', 'Assists', 'Steal', 'Block', 'To'], index=range(2))
    cross_color_df.fillna("None", inplace=True)
else:
    if mode_select == "Alternate Universe" or mode_select == "Medal Board":
        week_options = weeks_list
        week_select = st.sidebar.selectbox("Select a week", week_options)
    cross_points_df = pd.DataFrame(columns=['Team_Name', 'Score', 'FG', 'FT', 'threePtm', 'Points', 'Rebound', 'Assists', 'Steal', 'Block', 'To'], index=range(16)) 
    cross_color_df = pd.DataFrame(columns=['Team_Name', 'Score', 'FG', 'FT', 'threePtm', 'Points', 'Rebound', 'Assists', 'Steal', 'Block', 'To'], index=range(16))
    cross_color_df.fillna("None", inplace=True)

week_team_stats = pd.DataFrame(columns=['Team_Name', 'FGM', 'FGA', 'FG', 'FTM', 'FTA', 'FT', 'threePtm', 'Points', 'Rebound', 'Assists', 'Steal', 'Block', 'To', 'Is_Major'],index=range(16))
total_team_stats = pd.DataFrame(columns=['Team_Name', 'FGM', 'FGA', 'FG', 'FTM', 'FTA', 'FT', 'threePtm', 'Points', 'Rebound', 'Assists', 'Steal', 'Block', 'To', 'Is_Major'],index=range(16))

other_team = []

def get_team_stats(team_name, major_bool = False):
    global other_team
    matchup_list_selector = ['0','1','2','3','4','5','6','7']
    team_switch = ['0','1']
    idx = 0
    for select in matchup_list_selector:
        for switch in team_switch:
            key = week_matchups[select]['matchup']['0']['teams'][switch]['team'][0][0]['team_key']
            if major_bool == True:
                major_team_key = teams_list[team_name]
                if key == major_team_key:
                    week_team_stats.loc[idx].Is_Major = True
                    other_team_idx = '1' if switch == '0' else '0'
                    other_team = week_matchups[select]['matchup']['0']['teams'][other_team_idx]['team'][0][2]['name']
                else:
                    week_team_stats.loc[idx].Is_Major = False
            else:
                week_team_stats.loc[idx].Is_Major = False
            week_team_stats.loc[idx].Team_Name = week_matchups[select]['matchup']['0']['teams'][switch]['team'][0][2]['name']

            fGfT = [0,2]
            count =0
            for p in fGfT:
                stat = week_matchups[select]['matchup']['0']['teams'][switch]['team'][1]['team_stats']['stats'][p]['stat']['value']
                stat = stat.split('/')
                if stat[0] == '': stat[0] = 0
                if stat[1] == '': stat[1] = 0
                week_team_stats.loc[idx].iloc[1+count*3] = int(stat[0])
                week_team_stats.loc[idx].iloc[2+count*3] = int(stat[1])
                try:
                    stat = float(int(stat[0]) / int(stat[1]))
                except:
                    stat = 0
                week_team_stats.loc[idx].iloc[3+count*3] = stat
                count += 1
                
            for s in range(4,11):
                stat = week_matchups[select]['matchup']['0']['teams'][switch]['team'][1]['team_stats']['stats'][s]['stat']['value']
                if stat == '': stat = 0
                week_team_stats.loc[idx].iloc[s+3] = int(stat)

            idx += 1

    return week_team_stats

def get_total_team_stats(team_name, major_bool = True):
    global week_matchups
    global total_team_stats
    global weekly_team_stats
    i=0
    for team in teams_list:
        total_team_stats.loc[i].Team_Name = team
        i += 1
    total_team_stats.fillna("0", inplace=True)

    for week in weeks_list:
        matchups = lg.matchups(week=week.split(' ')[1])
        week_matchups = matchups['fantasy_content']['league'][1]['scoreboard']['0']['matchups']
        weekly_team_stats = get_team_stats(team_select, major_bool=True)
        for index, row in weekly_team_stats.iterrows():
            for idx in range(0,16):
                if total_team_stats.loc[idx].Team_Name == row['Team_Name']:
                    total_team_stats.loc[idx].FGM = int(total_team_stats.loc[idx].FGM) + row['FGM']
                    total_team_stats.loc[idx].FGA = int(total_team_stats.loc[idx].FGA) + row['FGA']
                    total_team_stats.loc[idx].FTM = int(total_team_stats.loc[idx].FTM) + row['FTM']
                    total_team_stats.loc[idx].FTA = int(total_team_stats.loc[idx].FTA) + row['FTA']
                    total_team_stats.loc[idx].threePtm = int(total_team_stats.loc[idx].threePtm) + row['threePtm']
                    total_team_stats.loc[idx].Points = int(total_team_stats.loc[idx].Points) + row['Points']
                    total_team_stats.loc[idx].Rebound = int(total_team_stats.loc[idx].Rebound) + row['Rebound']
                    total_team_stats.loc[idx].Assists = int(total_team_stats.loc[idx].Assists) + row['Assists']
                    total_team_stats.loc[idx].Steal = int(total_team_stats.loc[idx].Steal) + row['Steal']
                    total_team_stats.loc[idx].Block = int(total_team_stats.loc[idx].Block) + row['Block']
                    total_team_stats.loc[idx].To = int(total_team_stats.loc[idx].To) + row['To']
                    total_team_stats.loc[idx].Is_Major = row['Is_Major']
                    break
    for idx in range(0,16):        
        total_team_stats.loc[idx].FG = format(total_team_stats.loc[idx].FGM / total_team_stats.loc[idx].FGA , '.3f')
        total_team_stats.loc[idx].FT = format(total_team_stats.loc[idx].FTM / total_team_stats.loc[idx].FTA , '.3f')
    
    return total_team_stats

def calculate_weekly_score(t1,t2,idx):
    t1 = pd.DataFrame(t1).reset_index(drop=True)
    t2 = pd.DataFrame(t2).transpose().reset_index(drop=True)
    global cross_color_df
    t1 = t1.drop(columns=['Team_Name','FGM','FGA','FTA','FTM','Is_Major'])
    t2 = t2.drop(columns=['Team_Name','FGM','FGA','FTA','FTM','Is_Major'])
    win=0
    lose=0
    tie=0

    for column in t1.columns:
        if column == 'To':
            if t1[column][0] < t2[column][0]:
                win += 1
                if idx == -1:
                    cross_color_df[column].loc[1] = "Win"
                else:
                    cross_color_df[column].loc[idx] = "Win"

            elif t1[column][0] > t2[column][0]:
                lose += 1
                if idx == -1:
                    cross_color_df[column].loc[1] = "Lose"
                else:
                    cross_color_df[column].loc[idx] = "Lose"
            else:
                tie += 1
                if idx == -1:
                    cross_color_df[column].loc[1] = "Tie"
                else:                
                    cross_color_df[column].loc[idx] = "Tie"
        else:
            if t1[column][0] > t2[column][0]:
                win += 1
                if idx == -1:
                    cross_color_df[column].loc[1] = "Win"
                else:                
                    cross_color_df[column].loc[idx] = "Win"
            elif t1[column][0] < t2[column][0]:
                lose += 1
                if idx == -1:
                    cross_color_df[column].loc[1] = "Lose"
                else:                
                    cross_color_df[column].loc[idx] = "Lose"
            else:
                tie += 1
                if idx == -1:
                    cross_color_df[column].loc[1] = "Tie"
                else:                
                    cross_color_df[column].loc[idx] = "Tie"
    return str(win) + "-" + str(lose) + "-" + str(tie)

def get_cross_map():
    global cross_points_df
    global cross_color_df
    global week_team_stats
    major_df = week_team_stats.loc[week_team_stats['Is_Major'] == True]
    major_df = major_df.reset_index(drop=True)
    cross_points_df.loc[0].Team_Name = major_df['Team_Name'][0]
    cross_points_df.loc[0].Score = "-"
    cross_points_df.loc[0].FG = format(major_df['FG'][0], '.3f')
    cross_points_df.loc[0].FT = format(major_df['FT'][0], '.3f')
    cross_points_df.loc[0].threePtm = major_df['threePtm'][0]
    cross_points_df.loc[0].Points = major_df['Points'][0]
    cross_points_df.loc[0].Rebound = major_df['Rebound'][0]
    cross_points_df.loc[0].Assists = major_df['Assists'][0]
    cross_points_df.loc[0].Steal = major_df['Steal'][0]
    cross_points_df.loc[0].Block = major_df['Block'][0]
    cross_points_df.loc[0].To = major_df['To'][0]

    idx =1
    for index, row in week_team_stats.iterrows():
        if row['Is_Major'] == False:
            cross_points_df.loc[idx].Team_Name = row['Team_Name']
            cross_points_df.loc[idx].Score = calculate_weekly_score(major_df, row, idx)
            cross_points_df.loc[idx].FG = format(row['FG'], '.3f')
            cross_points_df.loc[idx].FT = format(row['FT'], '.3f')
            cross_points_df.loc[idx].threePtm = row['threePtm']
            cross_points_df.loc[idx].Points = row['Points']
            cross_points_df.loc[idx].Rebound = row['Rebound']
            cross_points_df.loc[idx].Assists = row['Assists']
            cross_points_df.loc[idx].Steal = row['Steal']
            cross_points_df.loc[idx].Block = row['Block']
            cross_points_df.loc[idx].To = row['To']
            idx += 1
    return cross_points_df

def get_cross_map_matchup():

    global cross_points_df
    global cross_color_df
    global matchup_select
    global week_matchups

    for week in weeks_list:
        matchups = lg.matchups(week=week.split(' ')[1])
        week_matchups = matchups['fantasy_content']['league'][1]['scoreboard']['0']['matchups']
        weekly_team_stats = get_team_stats(team_select, major_bool = True)

        major_df = weekly_team_stats.loc[weekly_team_stats['Is_Major'] == True]
        major_df = major_df.reset_index(drop=True)

        cross_points_df.loc[0].Week = week
        cross_points_df.loc[0].Team_Name = major_df['Team_Name'][0]
        cross_points_df.loc[0].Score = "-"
        cross_points_df.loc[0].FG = format(major_df['FG'][0], '.3f')
        cross_points_df.loc[0].FT = format(major_df['FT'][0], '.3f')
        cross_points_df.loc[0].threePtm = major_df['threePtm'][0]
        cross_points_df.loc[0].Points = major_df['Points'][0]
        cross_points_df.loc[0].Rebound = major_df['Rebound'][0]
        cross_points_df.loc[0].Assists = major_df['Assists'][0]
        cross_points_df.loc[0].Steal = major_df['Steal'][0]
        cross_points_df.loc[0].Block = major_df['Block'][0]
        cross_points_df.loc[0].To = major_df['To'][0]
        
        for index, row in weekly_team_stats.iterrows():
            if row['Team_Name'] == matchup_select:
                cross_points_df.loc[1].Week = ""
                cross_points_df.loc[1].Team_Name = row['Team_Name']
                cross_points_df.loc[1].Score = calculate_weekly_score(major_df, row, -1)
                cross_points_df.loc[1].FG = format(row['FG'], '.3f')
                cross_points_df.loc[1].FT = format(row['FT'], '.3f')
                cross_points_df.loc[1].threePtm = row['threePtm']
                cross_points_df.loc[1].Points = row['Points']
                cross_points_df.loc[1].Rebound = row['Rebound']
                cross_points_df.loc[1].Assists = row['Assists']
                cross_points_df.loc[1].Steal = row['Steal']
                cross_points_df.loc[1].Block = row['Block']
                cross_points_df.loc[1].To = row['To']
        
        df_color_codes = cross_color_df.map(color_map.get)
        style_cross = cross_points_df.style.apply(apply_color, colors=df_color_codes, axis=None)
        st.dataframe(style_cross, height=109, use_container_width=True)
        
    return cross_points_df

def ewlt_get(cross_map):
    vals = cross_map.loc[1:].Score.tolist()
    ewlt = {}
    w,l,t = 0,0,0
    for wlt in vals:
        wlt = wlt.split('-')
        w = w + int(wlt[0])
        l = l + int(wlt[1])
        t = t + int(wlt[2])
    w = w / len(vals)
    l = l / len(vals)
    t = t / len(vals)
    ewlt['Win'] = w
    ewlt['Lose'] = l
    ewlt['Tie'] = t
    return ewlt

color_map = {
    'Win': '#006400',
    'Lose': '#800000',
    'Tie': '#9ACD32',
    'None': '#0E1117',
    'Match': "#00008B"
}

color_map_total = {
        'None': '#0E1117',
        'Match': "#00008B"
}

def update_other_team_color():
    global cross_color_df
    global cross_points_df
    global other_team

    idx = cross_points_df[cross_points_df['Team_Name'] == other_team].index
    cross_color_df.loc[idx, 'Team_Name'] = "Match"
    cross_color_df.loc[idx, 'Score'] = "Match"

def apply_color(dataframe, colors):
    styled_df = pd.DataFrame('', index=dataframe.index, columns=dataframe.columns)
    for row in styled_df.index:
        for col in styled_df.columns:
            styled_df.at[row, col] = f'background-color: {colors.at[row, col]}'
    return styled_df

def render_medal_board():
    global week_matchups
    week_matchups = lg.matchups(week=week_select.split(' ')[1])['fantasy_content']['league'][1]['scoreboard']['0']['matchups']
    weakly_leaderboard = get_team_stats(team_select, major_bool = True)

    #matchups = lg.matchups(week_select.split(' ')[1])['fantasy_content']['league'][1]['scoreboard']['0']['matchups']
    #print("Match count" + str(matchups['count']))
    #league_matchups_list = []
    #for i in range(matchups['count']):
    #    #display(pd.json_normalize(matchupss[m]['matchup']))
    #    #print(matchups[str(i)]['matchup']['0'])
    #    teams = matchups[str(i)]['matchup']['0']['teams']
    #    for t in range(teams['count']):
    #        val_list = []
    #        #print(teams[str(t)]['team'][0][2]) #team name
    #        team_data = [teams[str(t)]['team'][0][2]['name']]
    
    #       for s in teams[str(t)]['team'][1]['team_stats']['stats']:
    #            team_data.append(str(s['stat']['value']))

    #        league_matchups_list.append(team_data)

    #weakly_leaderboard=pd.DataFrame(league_matchups_list,columns=['TeamName','FG','FG%','FT','FT%','3Points','Points','Reb','Ast','St','Blk','To' ]).astype({'TeamName':'object','FG':'object','FG%':'float64','FT':'object','FT%':'float64','3Points':'int64','Points':'int64','Reb':'int64','Ast':'int64','St':'int64','Blk':'int64','To':'int64'})
    
    categories = ['threePtm','Points','Rebound','Assists','Steal','Block']
    
    for c in ['FG', 'FT']:
        temp = weakly_leaderboard.sort_values(c,ascending=False).reset_index(drop=True)
        #temp[c+' '] = temp[c].round(4).astype(str)
        temp[c+' ']  = temp[c].apply(lambda x: '{0:.3f}'.format(x))
        temp[c+' '][0] = "{:.3f}".format(temp[c][0]) + Gold_Medal
        temp[c+' '][1] = "{:.3f}".format(temp[c][0])  + Silver_Medal
        temp[c+' '][2] = "{:.3f}".format(temp[c][0])  + Bronze_Medal
        weakly_leaderboard = temp.replace(np.nan,'')

    for c in categories:
        temp = weakly_leaderboard.sort_values(c,ascending=False).reset_index(drop=True)
        temp[c+' '] = temp[c]
        temp[c+' '][0] = str(temp[c][0]) + Gold_Medal
        temp[c+' '][1] = str(temp[c][1]) + Silver_Medal
        temp[c+' '][2] = str(temp[c][2]) + Bronze_Medal
        weakly_leaderboard = temp.replace(np.nan,'')
    temp = weakly_leaderboard.sort_values('To',ascending=True).reset_index(drop=True)
    temp['To '] = temp['To']
    temp['To '][0] =  str(temp['To'][0]) + Gold_Medal
    temp['To '][1] =  str(temp['To'][1]) + Silver_Medal
    temp['To '][2] =  str(temp['To'][2]) + Bronze_Medal
    weakly_leaderboard = temp.replace(np.nan,'')
    
    Total_Medals = []
    Total_Medals_Count = []
    for i in range(len(weakly_leaderboard)):
        g_count=0
        s_count=0
        b_count = 0
        for index, value in weakly_leaderboard.iloc[i].items():
            if Gold_Medal in str(value):
                g_count +=1
            if Silver_Medal in str(value):
                s_count +=1
            if Bronze_Medal in str(value):
                b_count +=1
        Total_Medals_Count.append(g_count * 1.03 + s_count * 1.02 + b_count * 1.01)
        Total_Medals.append(g_count * Gold_Medal + s_count * Silver_Medal + b_count * Bronze_Medal)
    weakly_leaderboard['Total'] = pd.Series(Total_Medals)
    weakly_leaderboard['MedalCount'] = pd.Series(Total_Medals_Count)
    weakly_leaderboard = weakly_leaderboard.sort_values('MedalCount',ascending=False,ignore_index=True)
    weakly_leaderboard = weakly_leaderboard.drop('MedalCount', axis=1)
    weakly_leaderboard = weakly_leaderboard.drop(columns=['FGM','FGA','FG','FTM','FTA','FT','threePtm','Points','Rebound','Assists','Steal','Block','To','Is_Major'])
    st.dataframe(weakly_leaderboard, height=600, use_container_width=True)

if mode_select == "Alternate Universe":
    matchups = lg.matchups(week=week_select.split(' ')[1])
    week_matchups = matchups['fantasy_content']['league'][1]['scoreboard']['0']['matchups']
    weekly_team_stats = get_team_stats(team_select, major_bool = True)
    get_cross_map()
    update_other_team_color()
    df_color_codes = cross_color_df.map(color_map.get)
    style_cross = cross_points_df.style.apply(apply_color, colors=df_color_codes, axis=None)
    st.dataframe(style_cross, height=600, use_container_width=True)
    ##Expected WLT eWLT Calculate
    ewlt_map = ewlt_get(cross_points_df)
    st.write( team_select + " " +  week_select + " expected win-lose-tie value (eWLT) is : " + format(ewlt_map["Win"], '.2f') + "-" + format(ewlt_map["Lose"], '.2f') + "-" + format(ewlt_map["Tie"], '.2f'))

elif mode_select == "Power Rankings":
    mini_skirt_df = pd.DataFrame(columns=['Team_Name', 'totaleWLT', 'avgeWLT', 'Score'], index=range(16))
    color_skirt_df = pd.DataFrame(columns=['Team_Name', 'totaleWLT', 'avgeWLT', 'Score'], index=range(16))
    color_skirt_df.fillna("None", inplace=True)

    hard_dict = {}
    for week in weeks_list:
        matchups = lg.matchups(week=week.split(' ')[1])
        week_matchups = matchups['fantasy_content']['league'][1]['scoreboard']['0']['matchups']
        weekly_team_stats = get_team_stats("", major_bool=False)

        for team in teams_list:
            chg_idx = week_team_stats[weekly_team_stats['Team_Name'] == team].index
            weekly_team_stats.loc[chg_idx, 'Is_Major'] = True
            map = get_cross_map()
            weekly_team_stats.loc[chg_idx, 'Is_Major'] = False
            ewlt_map = ewlt_get(cross_points_df)
            if team not in hard_dict:
                hard_dict[team] = {}
            hard_dict[team][week] = {
                'Win': ewlt_map['Win'],
                'Lose': ewlt_map['Lose'],
                'Tie': ewlt_map['Tie'],
            }
    aggregate_scores = {}

    for team, weeks in hard_dict.items():
        win_total = 0
        lose_total = 0
        tie_total = 0
        num_weeks = len(weeks)

        for week, scores in weeks.items():
            if not scores['Tie'] == 9:
                win_total += scores['Win']
                lose_total += scores['Lose']
                tie_total += scores['Tie']

        aggregate_scores[team] = {
            'TWin': win_total,
            'TLose': lose_total,
            'TTie': tie_total,
            'AWin': win_total / num_weeks if num_weeks else 0,
            'ALose': lose_total / num_weeks if num_weeks else 0,
            'ATie': tie_total / num_weeks if num_weeks else 0,
            'Total': win_total + tie_total
        }
         
    idx = 0
    for team, scores in aggregate_scores.items():
        mini_skirt_df.loc[idx].Team_Name = team
        mini_skirt_df.loc[idx].totaleWLT = format(scores['TWin'], '.2f') + "-" + format(scores['TLose'],
                                                                                        '.2f') + "-" + format(
            scores['TTie'], '.2f')
        mini_skirt_df.loc[idx].avgeWLT = format(scores['AWin'], '.2f') + "-" + format(scores['ALose'],
                                                                                      '.2f') + "-" + format(
            scores['ATie'], '.2f')
        mini_skirt_df.loc[idx].Score = scores['Total']
        idx += 1

    mini_skirt_df = mini_skirt_df.sort_values(by=['Score'], ascending=False)
    mini_skirt_df = mini_skirt_df.reset_index(drop=True)
    mini_skirt_df['Score'] = mini_skirt_df['Score'].map('{:.2f}'.format)
    chg = mini_skirt_df[mini_skirt_df['Team_Name'] == team_select].index
    color_skirt_df.loc[chg] = "Match"
    df_color_codes = color_skirt_df.map(color_map_total.get)
    style_cross = mini_skirt_df.style.apply(apply_color, colors=df_color_codes, axis=None)
    st.dataframe(style_cross, height=600, use_container_width=True)
elif mode_select == "Medal Board":
    render_medal_board()

elif mode_select == "Alternate Universe - Matchups":

    get_cross_map_matchup()

    ##Expected WLT eWLT Calculate
    #ewlt_map = ewlt_get(cross_points_df)
    #st.write( team_select + " " +  week_select + " expected win-lose-tie value (eWLT) is : " + format(ewlt_map["Win"], '.2f') + "-" + format(ewlt_map["Lose"], '.2f') + "-" + format(ewlt_map["Tie"], '.2f'))

elif mode_select == "Box Plots":
    
    if sub_mode_select == "Box - Weekly" or sub_mode_select == "Box & SD - Weekly":
        matchups = lg.matchups(week=week_select.split(' ')[1])
        week_matchups = matchups['fantasy_content']['league'][1]['scoreboard']['0']['matchups']
        team_stats = get_team_stats(team_select, major_bool = True)
        title = " - Week "+week_select.split(' ')[1]
        if sub_mode_select == "Box - Weekly":
            boxMean = True
        else:
            boxMean = "sd"
    elif sub_mode_select == "Box - Total":
        team_stats = get_total_team_stats(team_select, major_bool = True)
        title = " - Total"
        boxMean = True
    #team_stats = team_stats.drop(columns=['FGM','FGA','FTA','FTM'])

    major_df = team_stats.loc[team_stats['Is_Major'] == True]
    major_df = major_df.reset_index(drop=True)

    categoies = {0: 'Team_Name', 1:'FG', 2:'FT', 3:'threePtm', 4:'Points', 5:'Rebound', 6:'Assists', 7:'Steal', 8:'Block', 9:'To'}

    for i in range(1, 10):
        fig = go.Figure()
        fig.add_trace(go.Box(y=team_stats[categoies[i]], name= categoies[i]+title, boxmean=boxMean))
        highlight_trace = go.Scatter(x=[major_df.loc[0].Team_Name],y=[major_df[categoies[i]][0]],mode='markers', marker=dict(size=10, color='red'),name=major_df[categoies[0]][0])
        fig.add_trace(highlight_trace)
        st.plotly_chart(fig, use_container_width=False, theme="streamlit")

elif mode_select == "Total Stats":
    
    color_total_df = pd.DataFrame(columns=['Team_Name', 'FGM', 'FGA', 'FG', 'FTM', 'FTA', 'FT', 'threePtm', 'Points', 'Rebound', 'Assists', 'Steal', 'Block', 'To'],index=range(16))    
    color_total_df.fillna("None", inplace=True)
    
    team_stats = get_total_team_stats(team_select, major_bool = True)
    team_stats = team_stats.drop(columns=['Is_Major'])
    
    chg = team_stats[team_stats['Team_Name'] == team_select].index
    color_total_df.loc[chg] = "Match"
    df_color_codes = color_total_df.map(color_map_total.get)
    style_cross = team_stats.style.apply(apply_color, colors=df_color_codes, axis=None)
    st.dataframe(style_cross, height=600, use_container_width=True)