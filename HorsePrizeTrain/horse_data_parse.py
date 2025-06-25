import json
import csv
import transfer_data
import numpy as np


with open('data/match_20.json', 'r') as f:
    horse_json_data = json.load(f)
# print(horse_json_data)


fieldnames = ['age', 'sex', 'colour', 'country', 'rating', 'price', 'careerPrizeMoney',
              'dam_age', 'dam_sex', 'dam_colour', 'dam_country', 'dam_rating', 'dam_price', 'dam_careerPrizeMoney',
              'sire_age', 'sire_sex', 'sire_colour', 'sire_country', 'sire_rating', 'sire_price', 'sire_careerPrizeMoney']


def get_horse_info(id: str):
    # Assume json_data is your list of horse dicts
    result = next(
        (horse for horse in horse_json_data if horse['id'] == id), None)
    return result


# def get_trainer_info(id: str):


def extract_training_data():
    training_data = []

    for horse in horse_json_data:
        id = horse.get('id')
        dam_id = horse.get('horseDam').get('id')
        sire_id = horse.get('horseSire').get('id')
        # trainer_id = horse.get('trainer').get('id')

        dam = get_horse_info(dam_id)
        sire = get_horse_info(sire_id)

        if (horse != None) and (dam != None) and (sire != None):
            age = transfer_data.age2int(horse.get('age'))
            sex = transfer_data.sex2int(horse.get('sex'))
            colour = transfer_data.colour2int(horse.get('colour'))
            country = transfer_data.country2int(horse.get('country'))
            rating = int(horse.get('rating')) / 100.0
            price = transfer_data.money2int(horse.get('Price'))
            prize = transfer_data.money2int(horse.get('careerPrizeMoney'))

            dam_age = transfer_data.age2int(dam.get('age'))
            dam_sex = transfer_data.sex2int(dam.get('sex'))
            dam_colour = transfer_data.colour2int(dam.get('colour'))
            dam_country = transfer_data.country2int(dam.get('country'))
            dam_rating = int(dam.get('rating')) / 100.0
            dam_price = transfer_data.money2int(dam.get('Price'))
            dam_prize = transfer_data.money2int(dam.get('careerPrizeMoney'))

            sire_age = transfer_data.age2int(sire.get('age'))
            sire_sex = transfer_data.sex2int(sire.get('sex'))
            sire_colour = transfer_data.colour2int(sire.get('colour'))
            sire_country = transfer_data.country2int(sire.get('country'))
            sire_rating = int(sire.get('rating')) / 100.0
            sire_price = transfer_data.money2int(sire.get('Price'))
            sire_prize = transfer_data.money2int(sire.get('careerPrizeMoney'))

            data = {
                'age': age,
                'sex': sex,
                'colour': colour,
                'country': country,
                'rating': rating,
                'price': price,
                'careerPrizeMoney': prize,
                'dam_age': dam_age,
                'dam_sex': dam_sex,
                'dam_colour': dam_colour,
                'dam_country': dam_country,
                'dam_rating': dam_rating,
                'dam_price': dam_price,
                'dam_careerPrizeMoney': dam_prize,
                'sire_age': sire_age,
                'sire_sex': sire_sex,
                'sire_colour': sire_colour,
                'sire_country': sire_country,
                'sire_rating': sire_rating,
                'sire_price': sire_price,
                'sire_careerPrizeMoney': sire_prize
            }
            training_data.append(data)

    return training_data


def process_money(json_data):
    horse_careerPrizeMoney = [horse.get('careerPrizeMoney')
                              for horse in json_data]
    dam_careerPrizeMoney = [horse.get('dam_careerPrizeMoney')
                            for horse in json_data]
    sire_careerPrizeMoney = [horse.get('sire_careerPrizeMoney')
                             for horse in json_data]

    horse_price = [horse.get('price')
                   for horse in json_data]
    dam_price = [horse.get('dam_price')
                 for horse in json_data]
    sire_price = [horse.get('sire_price')
                  for horse in json_data]

    total_careerPrizeMoney = sum(horse_careerPrizeMoney) + \
        sum(dam_careerPrizeMoney) + sum(sire_careerPrizeMoney)
    average_careerPrizeMoney = total_careerPrizeMoney / \
        (len(horse_careerPrizeMoney) +
         len(dam_careerPrizeMoney) + len(sire_careerPrizeMoney))

    total_price = sum(horse_price) + sum(dam_price) + sum(sire_price)
    average_price = total_price / \
        (len(horse_price) + len(dam_price) + len(sire_price))

    for i, horse in enumerate(json_data):
        horse_careerPrizeMoney = horse.get(
            'careerPrizeMoney') / average_careerPrizeMoney
        dam_careerPrizeMoney = horse.get(
            'dam_careerPrizeMoney') / average_careerPrizeMoney
        sire_careerPrizeMoney = horse.get(
            'sire_careerPrizeMoney') / average_careerPrizeMoney

        horse_price = horse.get('price') / average_price
        dam_price = horse.get('dam_price') / average_price
        sire_price = horse.get('sire_price') / average_price

        horse['careerPrizeMoney'] = horse_careerPrizeMoney
        horse['dam_careerPrizeMoney'] = dam_careerPrizeMoney
        horse['sire_careerPrizeMoney'] = sire_careerPrizeMoney

        horse['price'] = horse_price
        horse['dam_price'] = dam_price
        horse['sire_price'] = sire_price

    return json_data, average_careerPrizeMoney, average_price


def save_training_data(data, average_careerPrizeMoney, average_price):
    with open('output.csv', mode='w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    means = np.array([average_careerPrizeMoney, average_price])
    np.save("means.npy", means)


if __name__ == "__main__":
    training_data = extract_training_data()
    training_data, average_careerPrizeMoney, average_price = process_money(
        training_data)

    save_training_data(training_data, average_careerPrizeMoney, average_price)
    print(training_data, average_careerPrizeMoney, average_price)
