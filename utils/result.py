import pandas as pd 

from pathlib import Path
import os
import shutil

test_result_path = r"D:\auto_tools\github\yolo_recognition_rate_test\result\test_result.csv"

df = pd.read_csv(test_result_path)
df.columns = ["game_name", "image_path", "label_id", "light_effect_id","light_effect"]
df = df.fillna(-1)
df["label_id"] = df["label_id"].astype("int32")
df["light_effect_id"] = df["light_effect_id"].astype("int32")
df["model_check_result"] = "None"
df["light_check_result"] = "None"

groupby = df.groupby("game_name")

# expect  result 
config_path = r"D:\auto_tools\github\yolo_recognition_rate_test\config\game_config.csv"
game_config = pd.read_csv(config_path)

for game_name, actual_df in groupby:
    print(f">>>[info:] game name: {game_name}")
    # if game_name in ["Deceive_inc", "Final_Fantasy_VII_Rebirth", "Mario_Kart8",
    #                 "Monster_Hunter_Rise", "Ring_Fit_Adventure", "streetFighter6", "Hearthstone Model"]:
    #     continue
    expect_df = game_config[game_config.game_name == game_name]
    for index, row in actual_df.iterrows():
        print(f">>>[info:] image name: {row.image_path}")
        # expect result
        expect_model_id = Path(row["image_path"]).stem.split("-")[0]
        expect_label_name = expect_df[expect_df.label_id == int(expect_model_id)]["label_name"].to_list()[0]
        expect_light_id = expect_df[expect_df.label_id == int(expect_model_id)]["effect_id"].to_list()[0]

        # actual result 
        model_id = row["label_id"]
        light_effect_id = row["light_effect_id"]


        if int(expect_model_id) == model_id:
            df.loc[index, "model_check_result"] = "pass"
            pass_path = f"images_pass/{game_name}"
            # if not os.path.exists(pass_path):
            #     os.makedirs(pass_path)
            # shutil.copy(row["image_path"], pass_path)

        else:
            df.loc[index, "model_check_result"]  = "fail"
            error_path = f"images_error/{game_name}"
            # if not os.path.exists(error_path):
            #     os.makedirs(error_path)
            # shutil.copy(row["image_path"], error_path)

        if expect_light_id  == light_effect_id:
            df.loc[index, "light_check_result"] = "pass"
        else:
            df.loc[index, "light_check_result"] = "fail"

df.to_csv("result/test_result_check.csv", index=False)

results = df[df.model_check_result == "pass"].groupby("game_name").size()
print(results)