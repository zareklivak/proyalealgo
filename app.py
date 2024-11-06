import streamlit as st
import pandas as pd
import numpy as np
import random
import math
import matplotlib.pyplot as plt

default_disclaimer = """
<div style="font-family: Arial, sans-serif; font-size: 16px; color: #2E86C1; background-color: #E8F6F3; padding: 10px; border-radius: 5px;">
    <strong>Default Parameters:</strong> <br>
    Number of Players: 100 <br>
    Percentage of Losers: 15% <br>
    Distribution Percentage: 5% <br>
    Max Stake: $500 <br>
    Stake Decay Rate: 10.0 <br>
    Streak Decay Rate: 5.0
</div>
"""
st.markdown(default_disclaimer, unsafe_allow_html=True)

st.title("Lottery Simulation")

# Sidebar for sliders
st.sidebar.header("Adjust Simulation Parameters")
num_players = st.sidebar.slider("Number of Players", min_value=10, max_value=150000, value=100)
loser_percentage = st.sidebar.slider("Percentage of Losers", min_value=0, max_value=100, value=15)
distribution_percentage = st.sidebar.slider("Distribution Percentage", min_value=1, max_value=100, value=5)
max_stake = st.sidebar.slider("Max Stake", min_value=10, max_value=1000, value=500)

# Exponential decay rates for stakes and streaks
st.sidebar.header("Exponential Decay Rates")
stake_decay = st.sidebar.slider("Stake Decay Rate", min_value=5.0, max_value=25.0, value=10.0, step=0.1)
streak_decay = st.sidebar.slider("Streak Decay Rate", min_value=1.0, max_value=10.0, value=5.0, step=0.1)

# Fixed minimum stake
min_stake = 3

# Function to generate random players with exponentially decreasing stakes and streaks
def generate_players(num_players, min_stake, max_stake, stake_decay, streak_decay):
    players = []
    for i in range(num_players):
        # Generate stake and daily streak based on adjustable exponential decay rates
        stake = max(min_stake, int(random.expovariate(1 / (max_stake / stake_decay))))
        daily_streak = max(1, int(random.expovariate(1 / streak_decay)))
        players.append({"User": f"Player {i+1}", "Stake": stake, "Daily Streak": daily_streak})
    return players

# Function to calculate winning probabilities based on stake and streak
def calculate_probabilities(players, stake_log_base=3, streak_multiplier=0.3):
    total_weight = 0
    for player in players:
        stake_weight = math.log(player["Stake"], stake_log_base)
        streak_weight = player["Daily Streak"] * streak_multiplier
        player["Total Weight"] = stake_weight + streak_weight
        total_weight += player["Total Weight"]
    for player in players:
        player["Winning Probability"] = player["Total Weight"] / total_weight

# Function to select winners and distribute winnings
def distribute_winnings(players, winners_count, total_pool):
    winners = random.choices(players, weights=[p["Winning Probability"] for p in players], k=winners_count)
    total_winner_weight = sum(w["Total Weight"] for w in winners)
    for winner in winners:
        winner["Winning Amount"] = (winner["Total Weight"] / total_winner_weight) * total_pool
    return winners

# Calculate the number of winners based on loser percentage
winner_percentage = 100 - loser_percentage
num_winners = max(1, int(num_players * (winner_percentage / 100)))
num_distributed_winners = max(1, int(num_winners * (distribution_percentage / 100)))

# Generate players and calculate the total pool based on their stakes
players = generate_players(num_players, min_stake, max_stake, stake_decay, streak_decay)
total_pool = sum(player["Stake"] for player in players)
rewards_pool = total_pool * 0.15  # 15% of the total pool is for rewards
pool_after_fee = rewards_pool * 0.95  # Deduct 5% fee from rewards pool

# Calculate probabilities and select winners
calculate_probabilities(players)
winners = distribute_winnings(players, num_distributed_winners, pool_after_fee)

winners_df = pd.DataFrame(winners)[["User", "Stake", "Daily Streak", "Winning Amount"]]

left_column, right_column = st.columns([3, 2])

with left_column:
    st.subheader("Results Summary")
    st.write(f"Total Pool: ${total_pool:,.2f}")
    st.write(f"Rewards Pool (15% of Total): ${rewards_pool:,.2f}")
    st.write(f"Pool After Fee (5% Deduction): ${pool_after_fee:,.2f}")

    st.subheader("Winners")
    st.dataframe(winners_df, height=400, width=600)

with right_column:
    st.subheader("Distribution Graphs")

    stake_values = [player["Stake"] for player in players]
    fig, ax = plt.subplots()
    ax.hist(stake_values, bins=50, color="skyblue", edgecolor="black")
    ax.set_title("Distribution of Stakes")
    ax.set_xlabel("Stake")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)

    streak_values = [player["Daily Streak"] for player in players]
    fig, ax = plt.subplots()
    ax.hist(streak_values, bins=50, color="salmon", edgecolor="black")
    ax.set_title("Distribution of Daily Streaks")
    ax.set_xlabel("Daily Streak")
    ax.set_ylabel("Frequency")
    st.pyplot(fig)
