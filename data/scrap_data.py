import json


with open("data.json", 'r') as file:
    js = json.load(file)


print(js["mediawiki"]["page"][0])

print(len(js["mediawiki"]["page"]))

res = []
for i in js["mediawiki"]["page"]:
    if i["title"] not in res:
        res.append(i["title"])
print(res)