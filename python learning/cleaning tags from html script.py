#cleaning tags from html script
import re

html = '<a href="#">Click here</a>'
print(re.sub('<.*?>', '', html))
