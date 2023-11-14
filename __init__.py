"""main file"""
pbn_words = ["/MAGAZINE", "/NEWS", "/HEALTH", "/MUM", "/FASHION", "/CASINO",
                 "/DAILY", "/LIFESTYLE", "/CBD", "/GAMB", "/FOOD", "/GAMBLING",
                 "/REVIEW", "/LEGAL", "/UNIVERSITY", "/SCHOOL", "/TRAVEL", "/MEDICAL"]

saas_words = ["/SOFTWARE", "/PLATFORM", "/SERVICE", "/TOOL", "/PRICING",
                "/SOLUTION", "/MAKER", "/GENERATOR", "/CREATOR", "/PRICE"
                "/BUILDER", "/FINDER", "/TRACKER", "/AGENCY", "/COMPANY"]

pbn_words = [i.lower() for i in pbn_words]
saas_words = [i.lower() for i in saas_words]

print(pbn_words)
print(saas_words)