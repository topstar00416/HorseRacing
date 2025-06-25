import os
import glob
import torch
import numpy as np
import pandas as pd
from horse_prize_regressor import HorsePrizeRegressor
import transfer_data


means = np.load("means.npy")
average_careerPrizeMoney = means[0]
average_price = means[1]

horse = {
    "age": "3YO",
    "sex": "Filly",
    "colour": "Bay",
    "country": "NZ",
    "rating": 0,
    "price": "$170,000",
    "dam_age": "12YO",
    "dam_sex": "Mare",
    "dam_colour": "Bay",
    "dam_country": "NZ",
    "dam_rating": 0,
    "dam_price": 0,
    "dam_careerPrizeMoney": "$0",
    "sire_age": "12YO",
    "sire_sex": "Horse",
    "sire_colour": "Bay",
    "sire_country": "(NZ)",
    "sire_rating": 105,
    "sire_price": 0,
    "sire_careerPrizeMoney": "$992,250"
}

age = transfer_data.age2int(horse.get('age'))
sex = transfer_data.sex2int(horse.get('sex'))
colour = transfer_data.colour2int(horse.get('colour'))
country = transfer_data.country2int(horse.get('country'))
rating = int(horse.get('rating')) / 100.0
price = transfer_data.money2int(horse.get('price')) / average_price

dam_age = transfer_data.age2int(horse.get('dam_age'))
dam_sex = transfer_data.sex2int(horse.get('dam_sex'))
dam_colour = transfer_data.colour2int(horse.get('dam_colour'))
dam_country = transfer_data.country2int(horse.get('dam_country'))
dam_rating = int(horse.get('dam_rating')) / 100.0
dam_price = transfer_data.money2int(horse.get('dam_price')) / average_price
dam_prize = transfer_data.money2int(
    horse.get('dam_careerPrizeMoney')) / average_careerPrizeMoney

sire_age = transfer_data.age2int(horse.get('sire_age'))
sire_sex = transfer_data.sex2int(horse.get('sire_sex'))
sire_colour = transfer_data.colour2int(horse.get('sire_colour'))
sire_country = transfer_data.country2int(horse.get('sire_country'))
sire_rating = int(horse.get('sire_rating')) / 100.0
sire_price = transfer_data.money2int(horse.get('sire_price')) / average_price
sire_prize = transfer_data.money2int(
    horse.get('sire_careerPrizeMoney')) / average_careerPrizeMoney


X_new = np.array([age, sex, colour, country, rating, price,
                  dam_age, dam_sex, dam_colour, dam_country, dam_rating, dam_price, dam_prize,
                  sire_age, sire_sex, sire_colour, sire_country, sire_rating, sire_price, sire_prize])
inputs = torch.tensor([X_new], dtype=torch.float32)


save_dir = "checkpoints"
model_files = glob.glob(os.path.join(save_dir, "horse_*.pth"))
if not model_files:
    raise FileNotFoundError("No checkpoints found in the directory!")

latest_model = max(model_files, key=os.path.getmtime)
print("Latest model:", latest_model)


# Load the Model & Weights
input_dim = 20  # replace with your feature count
model = HorsePrizeRegressor(input_dim)
model.load_state_dict(torch.load(latest_model, map_location="cpu"))
model.eval()


with torch.no_grad():
    output = model(inputs)
# print(output.item())

predicted_prize = output.item() * average_careerPrizeMoney
print("Predicted prize money: ", predicted_prize)
