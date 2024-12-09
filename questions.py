import random
import csv
import os

class Data_base():

    question = {}

    Correct_answer = {'Answer':[],
                      'Uncorrect':[]}

    Data = ["Когда",
        "Кто выйграл",
        "Кто являеться главным тренером",
        "Кто являетсья игроком",
        "Кто выйграл больше всего"
                ]
    
    def uncorrect(self,filename,titel):
        uncorrect_answers = []
        while len(uncorrect_answers) != 3:
            uncorect_choice = self.choiser_from_csv(filename,titel)
            if uncorect_choice not in self.Correct_answer['Answer']:
                if uncorect_choice not in uncorrect_answers:
                    uncorrect_answers.append(uncorect_choice)
        self.Correct_answer['Uncorrect'].extend(uncorrect_answers)
    
    def look(self,answer,filename,titel,another):
        with open(filename,'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row[titel] == answer:
                    self.Correct_answer['Answer'].append(row[another])

    def choiser_from_csv(self,filename,titel):
        _python_format_data = []
        _python_format_data.clear()
        with open(filename,'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                _python_format_data.append(row[titel])
        return random.choice(_python_format_data) 

    def choose_qestion(self):
        question = random.choice(range(0,len(self.Data)-1))
        return question
    
    def builder_questions(self):
        os.system('cls')
        question = None
        club = self.choiser_from_csv('league_champions.csv','winner').strip()
        player = self.choiser_from_csv('players_who_won.csv','winner').strip()
        club_eur = self.choiser_from_csv('league_euroupe.csv','winner').strip()
        retired_player = self.choiser_from_csv('players_retired.csv','winner').strip()
        choose = self.choose_qestion()
        if choose == 0:
            p_c = random.choice([club,player,club_eur,retired_player])
            DDT = None
            League = None
            if p_c == club:
                DDT = 'выйграл Лигу Чемпионов'
                League = 'League_champions.csv'
            elif p_c == club_eur:
                DDT = 'выйграл Лигу Европы'
                League = 'League_euroupe.csv'
            elif p_c == retired_player:
                DDT = 'завершил карьеру'
                League = 'players_retired.csv'
            else:
                DDT = 'выйграл Золотой мяч'
                League = 'players_who_won.csv'
            question = f"{self.Data[0]} {p_c} {DDT}?"
            print(question)
            self.look(p_c,League,'winner','year')
            self.uncorrect(League,'year')
        elif choose == 1:
            p_c = random.choice([club,club_eur,player])
            DDT = None
            League = None
            if p_c == club:
                DDT = 'Лигу Чемпионов'
                League = 'League_champions.csv'
            elif p_c == club_eur:
                DDT = 'Лигу Европы'
                League = 'League_euroupe.csv'
            else:
                DDT = 'Золотой мяч'
                League = 'players_who_won.csv'
            year = self.choiser_from_csv(League,'year')
            question = f"{self.Data[1]} {DDT} в {year} году?"
            print(question)
            self.look(year,League,'year','winner')
            self.uncorrect(League,'winner')
        elif choose == 2:
            coach = self.choiser_from_csv('coaches.csv','club')
            question = f'{self.Data[2]} {coach}?'
            print(question)
            self.look(coach,'coaches.csv','club','coach')
            self.uncorrect('coaches.csv','coach')
        elif choose == 3:
            player_ = self.choiser_from_csv('players.csv','club')
            question = f'{self.Data[3]} {player_}?'
            print(question)
            self.look(player_,'players.csv','club','player')
            self.uncorrect('players.csv','player')
        elif choose == 4:
            what = random.choice(['Лиг Чемпионов','Золотых мячей'])
            if what == 'Лиг Чемпионов':
                self.Correct_answer['Answer'].append('Karlo Ancelotti')
                self.uncorrect('coaches.csv','coach')
            else:
                self.Correct_answer['Answer'].append('Lionel Messi')
                self.uncorrect('players_who_won.csv','winner')
            question = f'{self.Data[4]} {what}?'
            print(question)
        return self.Correct_answer,question
        

        
        
            
D = Data_base()
D.builder_questions()
print(D.Correct_answer)


