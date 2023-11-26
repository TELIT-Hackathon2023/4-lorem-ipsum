import json
from preprocessing import preprocess

with open("data.json", 'r') as file:
    js = json.load(file)


def rec_save_text(f, data):
    if type(f) is str:
        # print(f)
        return
    for i in f.keys():
        if type(f[i]) is str:
            continue
        if type(f[i]) is dict:
            if "#text" in f[i].keys():
                data.append(f[i]["#text"])
            else:
                rec_save_text(f[i], data)
        elif type(f[i]) is list:
            for index, j in enumerate(f[i]):
                rec_save_text(j, data)




result_texts = []

rec_save_text(js, result_texts)
print(len(result_texts))
print(max(result_texts, key=lambda x:len(x)))
print(preprocess(result_texts[0]))


# preprocesed_array = []
# for text in result_texts:
#     preprocesed_array.append(preprocess(text))
#
# print(preprocesed_array[0])

