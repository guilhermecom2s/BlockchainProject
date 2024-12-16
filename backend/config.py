#This file will store global variables for the project

NANOSECONDS = 1 #it's my reference 
MICROSECONDS = 1000 * NANOSECONDS
MILLISECONDS = 1000 * MICROSECONDS
SECONDS = 1000 * MILLISECONDS

MINE_RATE = 4 * SECONDS #a block should be mined every 4 seconds

STARTING_BALANCE = 1000 #Having a higher number will make it easir to realize experiments in the future

MINING_REWARD = 50
MINING_REWARD_INPUT = { 'address': '*--official-mining-reward--*' } #it's the system address that rewards miners