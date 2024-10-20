from datetime import datetime
import sqlite3

# Du kommer se platshållare såsom (?) i vissa metoder, detta är för att förhindra SQL-injektion
# Detta hindrar användare från att skicka skadlig kod via inputs.
# Exempel på SQL-injektion: Harry Potter; DROP TABLE böcker; --

class Bibliotek:
    def __init__(self) -> None:
        # Skapa anslutning till databasen när objektet skapas
        self.connect = sqlite3.connect("bibliotek.db") # Ansluter till databasen
        self.cursor = self.connect.cursor() # Skapar cursor OBJEKT för att köra SQL kommandon

    def låna(self):
            # Hämtar alla böcker som har status icke utlånad
            self.cursor.execute("SELECT * FROM böcker WHERE utlånad = 0")
            tillgängliga_böcker = self.cursor.fetchall() # Vi lagrar en lista i variabeln med alla böcker som inte är utlånade

            # Ifall det inte finns några element i listan "tillgängliga_böcker" så skickas du ut till huvudmenyn.
            if not tillgängliga_böcker:
                print ("Det finns inga böcker att låna.")
                return

            if tillgängliga_böcker:
                print ("Tillgängliga böcker att låna:")
                for bok in tillgängliga_böcker:
                    print(f"ID: {bok[0]}, Titel: {bok[1]}, Författare: {bok[2]}, Kategori: {bok[3]}")

            # Be användaren om boktitel och låna ut den om den finns
            titel = input("\nAnge titeln på boken du vill låna: ").lower()

            # Vi går igenom alla titlar i tabellen "böcker". =? är en platshållare för variabeln titel.
                # "AND utlånad = 0" betyder att vi bara vill hämta böcker som inte är utlånade.
            self.cursor.execute("SELECT * FROM böcker WHERE LOWER(titel) = ? AND utlånad = 0", (titel,))

            # bok är en tuple som innehåller bokens data från databasen (ID, titel, författare, kategori, utlånad status).
            bok = self.cursor.fetchone()  # Hämta första matchande bok| fetchone() gör så att vi bara hämtar 1 bok även om det finns fler som matchar.

            if bok:
                # Ändrar boken till status utlånad, bok[0] hämtar bokens id från tabellen. t.ex så skulle bok[1] hämta titel.
                self.cursor.execute("UPDATE böcker SET utlånad = 1 WHERE id = ?", (bok[0],))
                self.connect.commit() # Sparar ändringarna permanent i databsen.
                
                # Skriver till loggfilen när boken lånas ut
                with open ("log.txt", "a", encoding="utf-8") as fil:
                    # Hämta aktuell tid och datum
                    nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    fil.write(f"Du har lånat '{bok[1]}' (ID: {bok[0]}) den {nu}\n")
                    
                print(f"Boken {bok[1]} är nu utlånad.") # Printar bok titeln är utlånad
            else:
                print(f"Boken {titel} är antingen utlånad eller finns inte i biblioteket.")


    def lämna_tillbaks(self):
        # Här hämtar vi allt från tabellen böcker. utlånad = 1 är alla böcker som är utlånade.
        self.cursor.execute("SELECT * FROM böcker WHERE utlånad = 1")
        lånade_böcker = self.cursor.fetchall() # Skapar en lista (lånade_böcker) med alla böcker som är lånade

        # Ifall det inte finns några böcker att lämna tillbaks så skickar vi tillbaks dig till huvudmenyn.
        if not lånade_böcker:
            print ("Det finns inga böcker att lämna tillbaks.")
            return 

        if lånade_böcker:
            print ("Alla böcker som är för tillfället lånade: ")
            for bok in lånade_böcker:
                print (f"ID: {bok[0]}, Titel: {bok[1]}, Författare: {bok[2]}, Kategori: {bok[3]}")

        titel = input ("Ange titel på boken du vill lämna tillbaks: ")
        self.cursor.execute("SELECT * FROM böcker WHERE LOWER(titel) = ? AND utlånad =  1", (titel,))

        bok = self.cursor.fetchone()

        if bok:
            # Uppdaterar boken med status ej lånad. "WHERE id" med parametern bok[0] gör så att endast denna bok med ett unikt ID ändrar status och inte flera som råkar ha samma namn.
            self.cursor.execute("UPDATE böcker SET utlånad = 0 WHERE id = ?", (bok[0],))
            self.connect.commit()

            print (f"Boken {bok[1]} har lämnats tillbaks.")

            with open ("log.txt", "a", encoding="utf-8") as fil:
                nu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                fil.write(f"Du har lämnat tillbaks '{bok[1]}' (ID: {bok[0]}) den {nu}\n")
                  
        else:
            print (f"Boken {titel} finns inte bland våra lånade böcker.")


    def lägg_till_bok(self):
        # Fråga användaren om titel, författare och kategori
        titel = input("Ange bokens titel: ")
        författare = input ("Ange bokens författare: ")
        kategori = input ("Ange kategorin för boken: ")
        
        # Lägger till nya boken i databastabellen "böcker" med hjälp utav cursor objektet.
        self.cursor.execute("INSERT INTO böcker (titel, författare, kategori, utlånad) VALUES (?, ?, ?, ?)",
                            (titel, författare, kategori, False))
        self.connect.commit() # Sparar ändringarna permanent i databastabellen

        # Informerar användare att boken har lagts till.
        print (f"Boken {titel} av {författare} har lagts till i biblioteket")


    def visa_böcker_per_kategori(self):
            kategori = input ("Ange kategori för böcker du vill se: ").lower()

            # SQLite i Python kräver att vi använder tuples för att skicka parametern till SQL, även om det bara är en, därav kommatecknet.
            self.cursor.execute("SELECT * FROM böcker WHERE LOWER(kategori) = ?", (kategori,))
            
            # Hämtar alla böcker från SQL tabellen som en lista av tuples
            böcker = self.cursor.fetchall() 

            # Om listan "böcker" inte är tom så körs koden i if blocket. Python tolkar en tom lista som FALSE och kör därmed inte if satsen.
            if böcker:
                print (f"Böcker i kategorin '{kategori.capitalize()}':")
                for bok in böcker:
                    print (f"ID: {bok[0]}, Titel: {bok[1]}, Författare: {bok[2]}, Kategori: {bok[3]}, Utlånad: {'Ja' if bok[4] else 'Nej'}") # Hämtar varje kolumn från tabellen

            # Om listan böcker är tom så körs else
            else:
                print (f"Vi hittade inga böcker i kategorin '{kategori}'")
            

    def visa_alla_böcker(self):
        
        # Hämtar alla böcker från databasen
        self.cursor.execute("SELECT * FROM böcker")
        
        # Hämtar alla böcker i en tuple 
        skriv_ut_alla_böcker = self.cursor.fetchall()

        # Om listan är tom, printa följande
        if not skriv_ut_alla_böcker:
            print (f"Det finns inga böcker, vårat bibliotek är tomt!")
            return
        
        # printar alla böcker
        for bok in skriv_ut_alla_böcker:
            print (f"ID: {bok[0]}, Titel: {bok[1]}, Författare: {bok[2]}, Kategori: {bok[3]}, Utlånad: {'Ja' if bok[4] else 'Nej'}")



    def ta_bort_böcker(self):
        
        # Hämtar alla böcker från databasen
        self.cursor.execute("SELECT * FROM böcker")

        # Hämtar alla böcker i en tuple 
        skriv_ut_alla_böcker = self.cursor.fetchall()

        # Om listan är tom, printa följande
        if not skriv_ut_alla_böcker:
            print (f"Det finns inga böcker att ta bort!")
            return

        # printar alla böcker
        for bok in skriv_ut_alla_böcker:
            print (f"ID: {bok[0]}, Titel: {bok[1]}, Författare: {bok[2]}, Kategori: {bok[3]}, Utlånad: {'Ja' if bok[4] else 'Nej'}")

        titel = input ("Ange titeln på boken du vill ta bort:\n").lower()
        
        # Söker efter boken med den angivna titeln (case-insenitivt)
        self.cursor.execute("SELECT * FROM böcker WHERE LOWER(titel) = ?", (titel,))
        bok = self.cursor.fetchone() # Hämtar första matchande boken från databasen

        # Om boken hittas, ta bort den från databasen
        if bok:
            self.cursor.execute("DELETE FROM böcker WHERE ID = ?", (bok[0],)) # Radera boken baserat på dess unika ID
            print(f"Boken {bok[1]} har tagits bort från biblioteket.")
            self.connect.commit() # Spara ändringar permanent

        else:
            print ("Det finns ingen bok med den titeln.")
        



