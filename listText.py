# coding: utf-8
import os
import datetime

# 중복 문장을 지움
def duplicateText(lines, write_file):
    print("HI!")

    lines = set(lines)
    remove = set()
    result = []
    for item in lines:
        if item not in remove:
            remove.add(item)
            result.append(item)

    return lines

# 날짜별로 정렬함
def sortText(lines, write_file):
    print("Hi!!")
    # 블로그용 - 파일에 맞게 x.split("\t")[0] 부분 수정할 것
    lines = sorted(lines, key=lambda x: datetime.datetime.strptime(x.split("\t")[0], '%Y.%m.%d. %H:%M'),
                   reverse=False)
    # 트위터용 - 파일에 맞게 x.split("\t")[0] 부분 수정할 것
    #lines = sorted(lines, key=lambda x: datetime.datetime.strptime(x.split("\t")[1], '%Y-%m-%d %H:%M:%S'),
    #               reverse=False)

    # sortText 쓸 때만 사용
    for line in lines:
        print(line)
        write_file.write(line + "\n")

if (__name__) == "__main__":
    # 폴더로 넣고 싶으면 밑에 있는 코드 (주석 처리 X)를 for문 안에 넣을 것
    # for inputFile in os.listdir("./res/blog2"):  # directory 지정
    #    outputFile = inputFile.split(".")[0] + "_output.txt"

    # read/write 파일 설정
    read_file = open(os.path.join("./res/blog","금천7(20081116).txt"), "r", encoding='UTF-8')
    write_file = open(os.path.join("./res/", "name.txt"), "w", encoding="UTF-8")

    lines = read_file.read().splitlines()

    lines = duplicateText(lines, write_file)
    sortText(lines, write_file)

    read_file.close()
    write_file.close()
