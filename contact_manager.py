import json
import os

CONTACTS_FILE = "contacts.json"

def load_contacts():
    """Loads contacts from the JSON file."""
    if not os.path.exists(CONTACTS_FILE):
        return []
    try:
        with open(CONTACTS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_contacts(contacts):
    """Saves the list of contacts to the JSON file."""
    with open(CONTACTS_FILE, "w") as f:
        json.dump(contacts, f, indent=4)

def add_contact(name, email):
    """Adds a new contact if the email doesn't already exist."""
    contacts = load_contacts()
    # Check for duplicates based on email
    for c in contacts:
        if c["email"].lower() == email.lower():
            return False, "Contact with this email already exists."
    
    contacts.append({"name": name, "email": email})
    save_contacts(contacts)
    return True, "Contact added successfully."

def delete_contact(email):
    """Deletes a contact by email."""
    contacts = load_contacts()
    initial_len = len(contacts)
    contacts = [c for c in contacts if c["email"].lower() != email.lower()]
    
    if len(contacts) < initial_len:
        save_contacts(contacts)
        return True
    return False
