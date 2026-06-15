from engine import insert, find, delete, list_collections

print(list_collections())

insert("users", {"name": "Alice", "country": "India"})
insert("users", {"name": "Bob", "country": "USA"})

results = find("users", {"country": "India"})
print("Results:", results)

deleted = delete("users", {"country": "India"})
print("Deleted:", deleted)
