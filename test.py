from datetime import datetime, date

now = datetime.now()
current_time = now.strftime("|%H:%M")

csvFileName = str(date.today()) + str(current_time) + '.csv'

print(csvFileName)