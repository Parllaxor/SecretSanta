import random

blocked_assignments = (
    ("Katie", "Trevor", "Porter"),
    ("Devin", "Kimarie"),
    ("Taylor", "Clarissa"),
    ("Trace", "Powy", "Ace"),
    ("Shayann", "Jayson")
)

def input_names():
    names = []
    with open ("names.txt", "r", encoding="utf-8") as file:
        for line in file:
            clean_name = line.strip().title()
            if clean_name:
                names.append(clean_name)

    return names

def is_blocked(giver, receiver):
    for group in blocked_assignments:
        if giver in group and receiver in group:
            return True

    return False

def assign_secret_santa(names):
    if len(names) < 2:
        raise ValueError("You need at least 2 people")

    attempt_counter = 0

    while attempt_counter < 1000:
        available_receivers = names[:]
        available_givers = names[:]
        random.shuffle(available_givers)
        random.shuffle(available_receivers)

        assignments = {}
        failed = False

        for giver in available_givers:
            valid_receivers = []

            for receiver in available_receivers:
                if giver == receiver:
                    continue
                if is_blocked(giver, receiver):
                    continue

                valid_receivers.append(receiver)

            if not valid_receivers:
                failed = True
                break

            receiver = random.choice(valid_receivers)
            assignments[giver] = receiver
            available_receivers.remove(receiver)

        if not failed:
            return assignments

        attempt_counter += 1

    raise ValueError("Could not find a valid Secret Santa arrangement")

def save_results(assignments):
    with open("output.txt", "w", encoding="utf-8") as file:
        for giver, receiver in assignments.items():
            file.write(f'"{giver}": "{receiver}"\n')

if __name__ == "__main__":
    names = input_names()
    secret_santa = assign_secret_santa(names)
    save_results(secret_santa)
    print("Secret Santa results saved to output")