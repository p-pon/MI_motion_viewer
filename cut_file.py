file = r"C:\Users\pavel\PycharmProjects\MI_motion\IMU\drive_2.csv"
with open(file, 'r') as fin:
    with open(file[:-4]+"_cut.csv", "a")as fout:
        for line in fin:
            # floatLine = list(map(float, line.split(";")))
            # if floatLine[6] != 0:
            if line.split(";")[6] != '0':
                fout.write(line)

