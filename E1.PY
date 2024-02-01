import streamlit as st
import pyrebase
import uuid
import os
import random
import time
import model
import pandas as pd


# Function to generate random player ID between 1 and 100
playersToSell=[]
def getPlayersToSell():
    for rownum,row in model.data.iterrows():
        if model.data['retained_players'][rownum]==0 and model.data['retired_player'][rownum]==0:
            playersToSell.append(rownum+1)
   # random.shuffle(playersToSell)

 

    

# Function to generate random player price between 50 and 100
def generate_player_price():
    return round(random.uniform(50, 100), 2)

# Function to send data to Firebase
    

# Initialize Pyrebase
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

    app_name = "organiser"

    # Create a Pyrebase app instance
    firebase = pyrebase.initialize_app(config=firebase_config)

    return firebase

# Call the initialization function
firebase = initialize_pyrebase()

# Get a reference to the Firebase Realtime Database
db = firebase.database()


# Streamlit UI
st.title("IPL AUCTIONEER")

# Generate random player ID and price
getPlayersToSell()
index=0
#player_id = st.select_slider('Select Player ID', options=playersToSell)
current_index = st.session_state.get("current_index", 0)

    # Display the current element

    # Create a button to move to the next element
if st.button("Next Player"):
        # Increment the index
    #st.write(f"Current Element: {playersToSell[st.session_state.current_index]}")
    current_index = (st.session_state.current_index + 1) % len(playersToSell)




    # Update the session state
st.session_state.current_index = current_index


player_id=playersToSell[st.session_state.current_index]
#st.write(playersToSell[index],"")
price_minima=model.data['base_price_in_lakhs'][player_id-1]
st.dataframe(model.data[player_id-1:player_id],hide_index=True)
player_price = st.select_slider('Select Price', options=list(range(price_minima, 3001,10)))


# Display the generated player data
#st.write(f"Generated Player ID: {player_id}")

#st.write(f"Generated Player Price: ${player_price}")

if st.button("Display to Teams","buttonnnn"):
    # Send player data to Firebase
    db.child("Current Bid").child('player_id').set(player_id)
    db.child("Current Bid").child('player_price').set(player_price)
    db.child("Current Bid").child('soldTo').set("Unsold")

    st.success("Player shown to Teams!")
    


st.markdown("")
st.markdown("")
st.markdown("")

selected_team = st.selectbox("Select Team to Mark as Sold", ["CSK", "RCB", "MI","RR","SRH","KKR","PK","DC","GT","LSG"])

if st.button("Mark Player as Sold","button2"):
    # Perform actions based on the selected team
    db.child("Current Bid").child('soldTo').set(selected_team)
    st.success(f"Player marked as sold to {selected_team}")
    #playersToSell.remove(player_id)
    st.session_state.next_element_button_clicked=True

    st.session_state.current_index+=1
    selected_team=None
if st.button("Mark Player as Unsold"):
    db.child("Current Bid").child('soldTo').set("Unsold")
    st.session_state.next_element_button_clicked=True
    st.session_state.current_index+=1
    selected_team=None



# Display actions from each team
st.title("Actions from Teams:")
teams = ["CSK", "RCB", "MI","RR","SRH","KKR","PK","DC","GT","LSG","END"]

#########display action for each team
while True:
    
    for team in teams:
        if team=="END" :
            st.write("END")
            continue

        action = db.child('Auction').child(player_id).child(player_price).child(f"{team}_action").get().val()
        st.write(f"Current Action for {team}: {action}")


        #time.sleep(0.5)
    
    st.experimental_rerun()
###############################

