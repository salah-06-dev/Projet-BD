import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Connexion à la base de données
def get_connection():
    return sqlite3.connect('hotel.db')

# Fonctions d'accès aux données
def get_reservations():
    conn = get_connection()
    query = '''SELECT r.Id_Reservation, c.Nom_complet, h.Ville, 
                      r.Date_arrivee, r.Date_depart, ch.Numero, tc.Type
               FROM Reservation r
               JOIN Client c ON r.Id_Client = c.Id_Client
               JOIN Chambre_Reservation cr ON r.Id_Reservation = cr.Id_Reservation
               JOIN Chambre ch ON cr.Id_Chambre = ch.Id_Chambre
               JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel
               JOIN Type_Chambre tc ON ch.Id_Type = tc.Id_Type'''
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_clients():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Client", conn)
    conn.close()
    return df

def get_available_rooms(start_date, end_date):
    conn = get_connection()
    query = '''SELECT ch.Id_Chambre, ch.Numero, ch.Etage, tc.Type, tc.Tarif, h.Ville 
               FROM Chambre ch
               JOIN Type_Chambre tc ON ch.Id_Type = tc.Id_Type
               JOIN Hotel h ON ch.Id_Hotel = h.Id_Hotel
               WHERE ch.Id_Chambre NOT IN (
                   SELECT cr.Id_Chambre
                   FROM Chambre_Reservation cr
                   JOIN Reservation r ON cr.Id_Reservation = r.Id_Reservation
                   WHERE (r.Date_arrivee <= ? AND r.Date_depart >= ?)
               )'''
    df = pd.read_sql(query, conn, params=(end_date, start_date))
    conn.close()
    return df

def add_client(nom, adresse, ville, code_postal, email, telephone):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO Client (Nom_complet, Adresse, Ville, Code_postal, Email, Telephone)
                 VALUES (?, ?, ?, ?, ?, ?)''', 
              (nom, adresse, ville, code_postal, email, telephone))
    conn.commit()
    conn.close()

def add_reservation(id_client, id_chambre, date_arrivee, date_depart):
    conn = get_connection()
    c = conn.cursor()
    try:
        # Ajout de la réservation
        c.execute('''INSERT INTO Reservation (Date_arrivee, Date_depart, Id_Client)
                     VALUES (?, ?, ?)''', (date_arrivee, date_depart, id_client))
        id_reservation = c.lastrowid
        
        # Lien avec la chambre
        c.execute('''INSERT INTO Chambre_Reservation (Id_Chambre, Id_Reservation)
                     VALUES (?, ?)''', (id_chambre, id_reservation))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        st.error(f"Erreur lors de l'ajout de la réservation: {e}")
        return False
    finally:
        conn.close()

def get_chambre_types():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Type_Chambre", conn)
    conn.close()
    return df

def get_hotels():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM Hotel", conn)
    conn.close()
    return df

# Interface Streamlit
def main():
    st.title("🏨 Système de gestion hôtelière")
    
    menu = st.sidebar.selectbox("Menu", [
        "Accueil",
        "📋 Réservations",
        "👥 Clients",
        "🛌 Chambres disponibles",
        "➕ Ajouter client",
        "➕ Ajouter réservation"
    ])
    
    if menu == "Accueil":
        st.header("Bienvenue dans le système de gestion hôtelière")
        st.image("https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80", 
                width=800, caption="Gestion complète de votre hôtel")
        
        st.markdown("""
        **Fonctionnalités disponibles:**
        - Consultation des réservations
        - Gestion des clients
        - Recherche de chambres disponibles
        - Ajout de nouvelles réservations
        - Ajout de nouveaux clients
        """)
        
    elif menu == "📋 Réservations":
        st.header("Liste des réservations")
        reservations = get_reservations()
        
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            date_debut = st.date_input("Filtrer par date d'arrivée")
        with col2:
            date_fin = st.date_input("Filtrer par date de départ")
        
        if date_debut and date_fin:
            mask = (reservations['Date_arrivee'] >= pd.to_datetime(date_debut).strftime('%Y-%m-%d')) & \
                   (reservations['Date_depart'] <= pd.to_datetime(date_fin).strftime('%Y-%m-%d'))
            reservations = reservations[mask]
        
        st.dataframe(reservations)
        
        # Statistiques
        st.subheader("Statistiques")
        col1, col2 = st.columns(2)
        col1.metric("Nombre total de réservations", len(reservations))
        if not reservations.empty:
            col2.metric("Durée moyenne (jours)", 
                       round((pd.to_datetime(reservations['Date_depart']) - 
                             (pd.to_datetime(reservations['Date_arrivee']))).dt.days.mean(), 1))
        
    elif menu == "👥 Clients":
        st.header("Liste des clients")
        clients = get_clients()
        st.dataframe(clients)
        
        # Statistiques clients
        st.subheader("Répartition géographique")
        ville_counts = clients['Ville'].value_counts()
        st.bar_chart(ville_counts)
        
    elif menu == "🛌 Chambres disponibles":
        st.header("Recherche de chambres disponibles")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Date d'arrivée", min_value=datetime.today())
        with col2:
            end_date = st.date_input("Date de départ", min_value=datetime.today())
        
        if start_date and end_date:
            if start_date >= end_date:
                st.error("La date d'arrivée doit être avant la date de départ")
            else:
                rooms = get_available_rooms(start_date, end_date)
                if rooms.empty:
                    st.warning("Aucune chambre disponible pour cette période")
                else:
                    st.dataframe(rooms)
                    
                    # Filtres supplémentaires
                    st.subheader("Filtrer les résultats")
                    types = rooms['Type'].unique()
                    selected_types = st.multiselect("Types de chambre", types, default=types)
                    
                    villes = rooms['Ville'].unique()
                    selected_villes = st.multiselect("Villes", villes, default=villes)
                    
                    filtered_rooms = rooms[
                        (rooms['Type'].isin(selected_types)) & 
                        (rooms['Ville'].isin(selected_villes))
                    ]
                    
                    st.dataframe(filtered_rooms)
    
    elif menu == "➕ Ajouter client":
        st.header("Ajouter un nouveau client")
        
        with st.form("client_form"):
            nom = st.text_input("Nom complet*", placeholder="Jean Dupont")
            adresse = st.text_input("Adresse*", placeholder="12 Rue de Paris")
            ville = st.text_input("Ville*", placeholder="Paris")
            code_postal = st.text_input("Code postal*", placeholder="75001")
            email = st.text_input("Email*", placeholder="jean.dupont@email.com")
            telephone = st.text_input("Téléphone*", placeholder="0612345678")
            
            submitted = st.form_submit_button("Enregistrer")
            if submitted:
                if nom and adresse and ville and code_postal and email and telephone:
                    add_client(nom, adresse, ville, code_postal, email, telephone)
                    st.success("Client ajouté avec succès!")
                else:
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
    
    elif menu == "➕ Ajouter réservation":
        st.header("Ajouter une nouvelle réservation")
        
        # Récupération des données nécessaires
        clients = get_clients()
        client_options = {row['Id_Client']: f"{row['Nom_complet']} ({row['Ville']})" 
                         for _, row in clients.iterrows()}
        
        with st.form("reservation_form"):
            # Sélection du client
            client_id = st.selectbox("Client*", options=list(client_options.keys()), 
                                   format_func=lambda x: client_options[x])
            
            # Dates de séjour
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Date d'arrivée*", min_value=datetime.today())
            with col2:
                end_date = st.date_input("Date de départ*", min_value=datetime.today())
            
            # Vérification des dates
            if start_date and end_date and start_date < end_date:
                rooms = get_available_rooms(start_date, end_date)
                if not rooms.empty:
                    room_options = {row['Id_Chambre']: f"Chambre {row['Numero']} ({row['Type']}, {row['Ville']}" 
                                   for _, row in rooms.iterrows()}
                    room_id = st.selectbox("Chambre*", options=list(room_options.keys()), 
                                         format_func=lambda x: room_options[x])
                else:
                    st.warning("Aucune chambre disponible pour cette période")
                    room_id = None
            else:
                st.warning("Veuillez sélectionner des dates valides")
                room_id = None
            
            submitted = st.form_submit_button("Enregistrer la réservation")
            if submitted and room_id:
                if add_reservation(client_id, room_id, start_date, end_date):
                    st.success("Réservation ajoutée avec succès!")
                    st.balloons()

if __name__ == "__main__":
    main()