import numpy as np
import uvicorn
from fastapi import FastAPI

from mmr.bayesian_rating_w3c import UpdateMmrRequestBody, update_after_game, UpdateMmrResponseBody
from teambalance.balance import BalanceTeamResponseBody, BalanceTeamRequestBody, Balance

app = FastAPI()

balance = Balance()

@app.post("/mmr/update")
async def update_mmr(body: UpdateMmrRequestBody) -> UpdateMmrResponseBody:
    for i, rd in enumerate(body.rds_list):
        if rd < 80:
            body.rds_list[i] *= 80/60.25
    
    for i, rating in enumerate(body.ratings_list):
        if rating < 0:
            body.ratings_list[i] = 0

    return update_after_game(body.ratings_list, body.rds_list, body.winning_team, body.number_of_teams)


@app.post("/team/balance")
async def balance_teams(body: BalanceTeamRequestBody) -> BalanceTeamResponseBody:
    for i, rd in enumerate(body.rds_list):
        if rd < 60.25:
            body.rds_list[i] = 60.25

    for i, rating in enumerate(body.ratings_list):
        if rating < 0:
            body.ratings_list[i] = 0

    return balance.find_best_game(np.array(body.ratings_list), np.array(body.rds_list), body.gamemode)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
