# adibot

A discord bot to manage various tasks for our Friday night games sessions.

## Getting Started

if using local docker compose, need to build and spin up to dev
```
docker compose build
docker compose up
```

## Deploy to gitea/Unraid

build both the images inside the Dockerfile
```
docker build -t 192.168.0.100:3000/dalby/adibot-web -target web .
docker build -t 192.168.0.100:3000/dalby/adibot-bot -target bot .
```

push both images up to the gitea registry
```
docker push 192.168.0.100:3000/dalby/adibot-web
docker push 192.168.0.100:3000/dalby/adibot-bot
```

## Command Ideas

/stats <discord-member>

Gives stats on member such as:
- total sessions attended
- total games played
- longest session streak

## Dashboard

The dashboard should have the following plots/charts:

- Total GM Count [DONE]
- DAYS SINCE GM [DONE]
- Attendance 
    - Longest Attendance Streak
    - Total Attendance Count
    - Proportion Attendance - pie chart
- Games
    - Longest Attendance Streak
    - Total Attendance Count
    - Proportion Attendance

- games_master_count
- attendance_count,.,//,,