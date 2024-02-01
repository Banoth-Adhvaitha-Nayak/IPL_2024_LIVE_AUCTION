import streamlit as st
import pyrebase
import time
import model
import pandas as pd
team_name="CSK"
if 'aucExc' not in st.session_state:
    st.session_state['aucExc'] = -1
if 'bought' not in st.session_state:
    st.session_state['bought'] = {}


def dfwork(t):
    st.subheader("Players To Buy")
    st.dataframe(t.playersToBidDf,hide_index=True)
    st.write(f"Fund Value in Lakhs: {t.fund}")

    currentPlayers=t.players
    st.subheader("Current Players")
    st.dataframe(pd.DataFrame(model.data.iloc[currentPlayers]),hide_index=True)
    st.write(f"Current Size: {len(currentPlayers)}")
    st.write(f"Batsmans: {len(t.squad['pure_batter'])}")
    st.write(f"Medium Pacers: {len(t.squad['pure_medium_pacer'])}")
    st.write(f"Spinners: {len(t.squad['pure_spinner'])}")
    st.write(f"All Rounders: {len(t.squad['all_rounder'])}")
    st.write(f"Overseas: {len(t.squad['overseas'])}")
    st.markdown("")
    st.markdown("")






def initialize_pyrebase():
    firebase_config = {
        "apiKey": "AIzaSyBFhDKdih5264eAspF7CW0jxi1a6sE2vu4",
        "authDomain": "iplauction-bc677.firebaseapp.com",
        "databaseURL": "https://iplauction-bc677-default-rtdb.firebaseio.com",
        "projectId": "iplauction-bc677",
        "storageBucket": "iplauction-bc677.appspot.com",
        "messagingSenderId": "347525357899",
        "appId": "1:347525357899:web:75a8e12cc0219c6bb2c8ce",
        "measurementId": "G-ZNWXS29YG0"
    }

    # Create a Pyrebase app instance
    firebase = pyrebase.initialize_app(config=firebase_config)

    return firebase

def receive_from_firebase():
    firebase = initialize_pyrebase()
    db = firebase.database()
    players_data = db.child("Current Bid").get()
    return players_data.val()

# Streamlit UI
st.title("Team"+" Dashboard")
####################################################################3
team_names = ['CSK', 'RR', 'RCB', 'MI','DC','PK','KKR','SRH','GT','LSG']

# Create a dropdown for selecting a team
selected_team = st.selectbox('Select a team:', team_names)
team_name=selected_team
#################helper to get squad batters bowlers
t=model.mainFunc(selected_team,25,[5,5,2,2,5,10],st.session_state.aucExc,st.session_state.bought)

    # Create a slider for selecting the team size
#selected_team_size = st.select_slider('Select team size:', options=list(range(20, 31)))
selected_batsman_size = st.select_slider('Batsmans:', options=list(range(len(t.squad['pure_batter']), 11)))
selected_medium_pacers_size = st.select_slider('Medium Pacers:', options=list(range(len(t.squad['pure_medium_pacer']), 11)))
selected_spinners_size = st.select_slider('Spinners:',options=list(range(len(t.squad['pure_spinner']), 11)))
selected_allrounder_size = st.select_slider('All Rounders:', options=list(range(len(t.squad['all_rounder']), 11)))
selected_wicket_keeper_size = st.select_slider('Wicket Keepers:', options=list(range(len(t.squad['wicket_keeper']), 11)))



total_sum=selected_allrounder_size+selected_batsman_size+selected_medium_pacers_size+selected_spinners_size+selected_wicket_keeper_size

    

####################################################################33
while True:

    ##############################3
    t=model.mainFunc(selected_team,total_sum,[selected_batsman_size,selected_medium_pacers_size,selected_spinners_size,selected_wicket_keeper_size,selected_allrounder_size,10],st.session_state.aucExc,st.session_state.bought)
    st.write(f"Estimated Team Size: {total_sum}")
    #st.write(st.session_state.aucExc)
    print("psopslwplp")
    print(st.session_state.aucExc)

   # dfwork(t)
    st.subheader("Players To Buy")
    columns = list(t.playersToBidDf.columns)
    columns = columns[:columns.index('sold_price')+1] + ['maxPrice'] + columns[columns.index('sold_price')+1:-1]
    if( not t.lpSuccess):
        st.write("Could Not Fetch Optimal Players : (")
    displayDF=t.playersToBidDf[columns]
    st.dataframe(displayDF,hide_index=True)

    st.write(f"Fund Value in Lakhs: {t.fund}")

    currentPlayers=t.players
    st.subheader("Current Players")
    st.dataframe(pd.DataFrame(model.data.iloc[currentPlayers]),hide_index=True)
    # st.write(f"Current Size: {len(currentPlayers)}")
    # st.write(f"Batsmans: {len(t.squad['pure_batter'])}")
    # st.write(f"Medium Pacers: {len(t.squad['pure_medium_pacer'])}")
    # st.write(f"Spinners: {len(t.squad['pure_spinner'])}")
    # st.write(f"All Rounders: {len(t.squad['all_rounder'])}")
    # st.write(f"Overseas: {len(t.squad['overseas'])}")
    st.write(f"Current Size: {len(currentPlayers)}&nbsp;&nbsp;&nbsp;Batsmans: {len(t.squad['pure_batter'])}&nbsp;&nbsp;&nbsp;Medium Pacers: {len(t.squad['pure_medium_pacer'])}&nbsp;&nbsp;&nbsp;Spinners: {len(t.squad['pure_spinner'])}&nbsp;&nbsp;&nbsp;All Rounders: {len(t.squad['all_rounder'])}&nbsp;&nbsp;&nbsp;Overseas: {len(t.squad['overseas'])}")

    st.markdown("")
    st.markdown("")



    # Receive data from Firebase
    received_data = receive_from_firebase()

    # Display received data
    player_id=0
    player_price=0
    if received_data:
        st.header("Auction Player Data:")
        
        player_id=received_data['player_id']
        player_price=received_data['player_price']
        st.dataframe(model.data[player_id-1:player_id],hide_index=True)
        print("nsiiwjiswismiwsisnwi")
        st.session_state.aucExc=player_id-1
        print(st.session_state.aucExc)


        st.write(f"Player ID: {player_id}, Player Price in Lakhs: {player_price}")
    else:
        st.warning("No player data found in the database.")

   

    # Buttons for bid and leave actions
    firebase = initialize_pyrebase()
    db = firebase.database()
    bid_button = st.button("BID!")
   # leave_button = st.button(f"{team_name}: Leave here")

    # Handle bid action
    if bid_button:
        if(t.fund>=player_price):
           db.child('Auction').child(player_id).child(player_price).child(f"{team_name}_action").set("Bid")
           #st.success("Bid at "+str(player_price))
        else:
            st.success("Insufficient Funds Left")

    # Handle leave action
   # if leave_button:
    #    db.child('Auction').child(player_id).child(player_price).child(f"{team_name}_action").set("Leave")
    # Refresh every 5 seconds
    time.sleep(0.1)

    # Clear the Streamlit cache to force a re-run and update the displayed data
    
    if team_name== db.child("Current Bid").child('soldTo').get().val():
      #  t.adder(player_id,player_price)
        st.subheader("Players Bought")
        bought=[]
        for p in t.players:
            if p not in t.retained_players:
                print("ok")
        st.session_state.bought[player_id-1]=player_price
        l=list(st.session_state.bought.keys())
        st.dataframe(model.data.iloc[l])
        st.write(f"Fund Left in Lakhs: {t.fund}")

        

        

   

    st.rerun()
