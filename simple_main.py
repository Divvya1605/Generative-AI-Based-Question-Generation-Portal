import os
import json
from datetime import datetime
from pdf_processor import PDFProcessor
from llm_engine import LLMQuestionEngine


def main():
    print("=" * 60)
    print("📚 SIMPLE PDF QUESTION GENERATOR (OFFLINE MODE)")
    print("=" * 60)

    # Get PDF path
    pdf_path = input("Enter PDF file path: ").strip()
    if not os.path.exists(pdf_path):
        print(f"Error: File not found: {pdf_path}")
        return

    # Create output folder
    os.makedirs("output", exist_ok=True)

    print("\n1. Processing PDF...")
    processor = PDFProcessor()
    pdf_data = processor.extract_text(pdf_path)

    print(f"   ✓ Pages: {pdf_data['total_pages']}")
    print(f"   ✓ Chunks: {len(pdf_data['chunks'])}")

    print("\n2. Initializing LLM (offline)...")
    llm = LLMQuestionEngine()

    print("\n3. Generating questions...")

    all_questions = {
        "MCQ": [],
        "Short Answer": [],
        "Long Answer": []
    }

    # Process up to first 3 chunks
    for i, chunk in enumerate(pdf_data["chunks"][:3]):
        print(f"   Chunk {i + 1}/3...")
        questions = llm.generate_questions(chunk["content"])

        for q_type in all_questions:
            for q in questions[q_type]:
                q["chunk"] = i + 1
                all_questions[q_type].append(q)

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_file = f"output/questions_{timestamp}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(all_questions, f, indent=2)

    text_file = f"output/questions_{timestamp}.txt"
    with open(text_file, "w", encoding="utf-8") as f:
        f.write("GENERATED QUESTIONS\n")
        f.write("=" * 50 + "\n\n")

        for q_type, questions in all_questions.items():
            if not questions:
                continue

            f.write(f"{q_type.upper()} QUESTIONS\n")
            f.write("-" * 50 + "\n")

            for i, q in enumerate(questions, 1):
                f.write(f"\nQ{i} (Chunk {q['chunk']}):\n")
                f.write(q["question"] + "\n")

            f.write("\n\n")

    print("\n" + "=" * 60)
    print("✅ DONE!")
    print(f"Questions saved to:")
    print(f"  • {json_file}")
    print(f"  • {text_file}")
    print("=" * 60)

    # Preview
    if all_questions["MCQ"]:
        print("\n📊 Preview (first MCQ):")
        print(all_questions["MCQ"][0]["question"])


if __name__ == "__main__":
    main()
