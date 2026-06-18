"""Student record manager for test scores and grade calculation."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List

DATA_FILE = "student_grades.txt"


@dataclass
class Student:
    name: str
    student_id: str
    test_scores: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    average: float = 0.0
    grade: str = "F"

    def __post_init__(self) -> None:
        self.update_stats()

    def update_stats(self) -> None:
        self.average = sum(self.test_scores) / len(self.test_scores)
        self.grade = self.calculate_grade()

    def calculate_grade(self) -> str:
        if self.average >= 90:
            return "A"
        if self.average >= 80:
            return "B"
        if self.average >= 70:
            return "C"
        if self.average >= 60:
            return "D"
        return "F"

    def set_scores(self, scores: List[float]) -> None:
        self.test_scores = scores
        self.update_stats()

    def to_pipe_line(self) -> str:
        return (
            f"{self.name}|{self.student_id}|"
            f"{self.test_scores[0]:.2f}|{self.test_scores[1]:.2f}|{self.test_scores[2]:.2f}|"
            f"{self.average:.2f}|{self.grade}\n"
        )

    @staticmethod
    def from_pipe_line(line: str) -> "Student":
        parts = line.strip().split("|")
        if len(parts) != 7:
            raise ValueError("Invalid record format")
        name, student_id, test1, test2, test3, _, _ = parts
        scores = [float(test1), float(test2), float(test3)]
        return Student(name=name, student_id=student_id, test_scores=scores)


def display_menu() -> None:
    print("\nStudent Records Menu")
    print("1. Add a new student")
    print("2. Update a student's test scores")
    print("3. Show all student records")
    print("4. Show class statistics")
    print("5. Search for a student by name")
    print("ESC. Exit")


def prompt_input(prompt: str) -> str:
    return input(prompt).strip()


def get_student_name() -> str:
    return prompt_input("Student name: ")


def get_student_id() -> str:
    return prompt_input("Student ID: ")


def get_test_score(test_number: int) -> float:
    while True:
        raw = prompt_input(f"Test {test_number} score (0-100): ")
        try:
            score = float(raw)
            if 0 <= score <= 100:
                return score
            print("Score must be between 0 and 100.")
        except ValueError:
            print("Invalid score. Enter a number between 0 and 100.")


def collect_three_scores() -> List[float]:
    return [get_test_score(i) for i in range(1, 4)]


def add_student(records: Dict[str, Student]) -> None:
    name = get_student_name()
    if not name:
        print("Error: Student name cannot be blank.")
        return

    student_id = get_student_id()
    if not student_id:
        print("Error: Student ID cannot be blank.")
        return

    if student_id in records:
        print(f"Error: Student ID '{student_id}' already exists.")
        return

    scores = collect_three_scores()
    student = Student(name=name, student_id=student_id, test_scores=scores)
    records[student_id] = student
    print(f"Added student '{name}' with ID '{student_id}' and average {student.average:.2f}.")


def update_scores(records: Dict[str, Student]) -> None:
    student_id = get_student_id()
    if student_id not in records:
        print(f"Error: Student ID '{student_id}' not found.")
        return

    scores = collect_three_scores()
    records[student_id].set_scores(scores)
    student = records[student_id]
    print(
        f"Updated scores for '{student.name}' ({student.student_id}). "
        f"New average is {student.average:.2f} and grade is {student.grade}."
    )


def show_student_records(records: Dict[str, Student]) -> None:
    if not records:
        print("No student records to display.")
        return

    headers = ["Name", "ID", "Test 1", "Test 2", "Test 3", "Average", "Grade"]
    widths = [20, 12, 8, 8, 8, 8, 7]
    header_row = " | ".join(f"{header:<{widths[i]}}" for i, header in enumerate(headers))
    separator = "-" * len(header_row)

    print(header_row)
    print(separator)
    for student in records.values():
        print(
            " | ".join(
                [
                    f"{student.name[:widths[0]-1]:<{widths[0]}}",
                    f"{student.student_id[:widths[1]-1]:<{widths[1]}}",
                    f"{student.test_scores[0]:<{widths[2]}.2f}",
                    f"{student.test_scores[1]:<{widths[3]}.2f}",
                    f"{student.test_scores[2]:<{widths[4]}.2f}",
                    f"{student.average:<{widths[5]}.2f}",
                    f"{student.grade:<{widths[6]}}",
                ]
            )
        )


def show_class_statistics(records: Dict[str, Student]) -> None:
    if not records:
        print("No student records available for statistics.")
        return

    averages = [student.average for student in records.values()]
    class_avg = sum(averages) / len(averages)
    highest = max(averages)
    lowest = min(averages)
    print(f"Class average: {class_avg:.2f}")
    print(f"Highest average: {highest:.2f}")
    print(f"Lowest average: {lowest:.2f}")


def search_student_by_name(records: Dict[str, Student]) -> None:
    query = prompt_input("Enter name to search: ").lower()
    if not query:
        print("Error: Search query cannot be blank.")
        return

    found = [student for student in records.values() if query in student.name.lower()]
    if not found:
        print(f"No student found matching '{query}'.")
        return

    print(f"Found {len(found)} student(s):")
    for student in found:
        print(
            f"Name: {student.name}, ID: {student.student_id}, "
            f"Scores: {student.test_scores[0]:.2f}, {student.test_scores[1]:.2f}, {student.test_scores[2]:.2f}, "
            f"Average: {student.average:.2f}, Grade: {student.grade}"
        )


def save_records(records: Dict[str, Student], filename: str = DATA_FILE) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as file:
            for student in records.values():
                file.write(student.to_pipe_line())
        print(f"Student records saved to '{filename}'.")
    except OSError as error:
        print(f"Error: Unable to save student records to '{filename}': {error}")


def load_records(filename: str = DATA_FILE) -> Dict[str, Student]:
    records: Dict[str, Student] = {}
    if not os.path.exists(filename):
        print(f"No existing record file found. A new file will be created at '{filename}'.")
        return records

    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, 1):
                raw = line.strip()
                if not raw:
                    continue
                try:
                    student = Student.from_pipe_line(raw)
                    records[student.student_id] = student
                except ValueError:
                    print(f"Warning: Skipping invalid record on line {line_number}.")
    except OSError as error:
        print(f"Error: Unable to read student records from '{filename}': {error}")
    return records


def main() -> None:
    records = load_records()
    print(f"Loaded {len(records)} student record(s) from '{DATA_FILE}'.")

    while True:
        display_menu()
        choice = prompt_input("Choose an option (1-5 or ESC to exit): ")
        if choice.upper() == "ESC":
            save_records(records)
            print("Exiting program. Goodbye!")
            break
        if choice == "1":
            add_student(records)
            save_records(records)
        elif choice == "2":
            update_scores(records)
            save_records(records)
        elif choice == "3":
            show_student_records(records)
        elif choice == "4":
            show_class_statistics(records)
        elif choice == "5":
            search_student_by_name(records)
        else:
            print("Invalid selection. Please enter 1-5 or ESC.")


if __name__ == "__main__":
    main()
