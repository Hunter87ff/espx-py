import asyncio
import os
from espx import ESPXClient
from espx.models import (
    BRLeaderboardPayload,
    LeaderboardRow,
    LeaderboardSocial
)

async def main() -> None:
    # Configuration
    BASE_URL = "http://localhost:8001"
    ACCESS_TOKEN = "testing-demo-token" # Usually provided in server config or env

    # Demo Team Data from leaderboard.ts
    team_data = [
        { "rank": "01", "name": "Spruce Esports", "matches": "12", "wins": "03", "pos_pts": "50", "kill_pts": "60", "total_pts": "110" },
        { "rank": "02", "name": "Team Open Source", "matches": "12", "wins": "02", "pos_pts": "45", "kill_pts": "52", "total_pts": "97" },
        { "rank": "03", "name": "Byte Brawlers", "matches": "12", "wins": "01", "pos_pts": "38", "kill_pts": "48", "total_pts": "86" },
        { "rank": "04", "name": "Pythonic Pros", "matches": "12", "wins": "01", "pos_pts": "35", "kill_pts": "40", "total_pts": "75" },
        { "rank": "05", "name": "Rust Raiders", "matches": "12", "wins": "00", "pos_pts": "30", "kill_pts": "38", "total_pts": "68" },
        { "rank": "06", "name": "Go Giants", "matches": "12", "wins": "00", "pos_pts": "25", "kill_pts": "30", "total_pts": "55" },
        { "rank": "07", "name": "Java Juggernauts", "matches": "12", "wins": "00", "pos_pts": "20", "kill_pts": "25", "total_pts": "45" },
        { "rank": "08", "name": "C++ Champions", "matches": "12", "wins": "00", "pos_pts": "15", "kill_pts": "20", "total_pts": "35" },
        { "rank": "09", "name": "Ruby Runners", "matches": "12", "wins": "00", "pos_pts": "10", "kill_pts": "15", "total_pts": "25" },
        { "rank": "10", "name": "PHP Phantoms", "matches": "12", "wins": "00", "pos_pts": "5", "kill_pts": "10", "total_pts": "15" },
        { "rank": "11", "name": "Swift Swarm", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "5", "total_pts": "5" },
        { "rank": "12", "name": "Kotlin Knights", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "13", "name": "Node Ninjas", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "14", "name": "Perl Pirates", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "15", "name": "Scala Spartans", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "16", "name": "Dart Demons", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "17", "name": "Haskell Hawks", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "18", "name": "Lua Legends", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "19", "name": "Erlang Eagles", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "20", "name": "Elixir Elite", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "21", "name": "Clojure Crew", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "22", "name": "F# Fighters", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "23", "name": "MATLAB Mavericks", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "24", "name": "Assembly Assassins", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" },
        { "rank": "25", "name": "Bash Bandits", "matches": "12", "wins": "00", "pos_pts": "0", "kill_pts": "0", "total_pts": "0" }
    ]

    # Convert to LeaderboardRow objects
    rows = [LeaderboardRow(**team) for team in team_data]

    # Prepare Payload
    payload = BRLeaderboardPayload(
        template="horizontal_blackyellow",
        teams=rows,
        organizer="LiFe Esports",
        eventname="SUMMER CUP S1",
        social=LeaderboardSocial(
            twitter="@organizer",
            instagram="@organizer",
            facebook="@organizer",
            youtube="@organizer"
        )
    )

    async with ESPXClient(base_url=BASE_URL, access_token=ACCESS_TOKEN) as client:
        print("Generating demo leaderboard...")
        try:
            result = await client.leaderboards.br.generate(payload, raw=True)

            output_path = "demo_leaderboard.png"
            with open(output_path, "wb") as f:
                f.write(result.require_content())

            print(f"Successfully generated pointtable: {os.path.abspath(output_path)}")
        except Exception as e:
            print(f"Error generating leaderboard: {e}")

if __name__ == "__main__":
    asyncio.run(main())
