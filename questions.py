import csv 

class Questions_maker():

    def dispetcher(self,num,topic,column_name='question'):
        for _ in range(1,num + 1):
            return self.Question_reader(topic,column_name)

    def correct(self,number):
        if int(number) == 1:
            return 'a1'
        elif int(number) == 2:
            return 'a2'
        elif int(number) == 3:
            return 'a3'
        else:
            return 'a4'
    
    def Question_reader(self,topic,column_name='text'):
        result = []
        with open(topic,'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                text = row[column_name]
                answer = row[self.correct(row['correct'])]
                correct = (answer,True)
                if row['a1'] != answer:
                    a1 = (row['a1'])
                    result.append(a1)
                if row['a2'] != answer:
                    a2 = (row['a2'])
                    result.append(a2)
                if row['a3'] != answer:
                    a3 = (row['a3'])
                    result.append(a3)
                if row['a4'] != answer:
                    a4 = (row['a4'])
                    result.append(a4)
                result.insert(0,correct)
        return(text,result)
                

Q = Questions_maker()

print(Q.Question_reader('questions.csv'))
                
