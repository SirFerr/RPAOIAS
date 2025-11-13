from demo_program import assemble_and_run_demo

# -----------------------------
#  Безадресная/Гарвард/Сумма элементов
# -----------------------------

if __name__ == "__main__":
    program, state = assemble_and_run_demo([5, -2, 112, 7], trace=True)
    print("\n--- Machine code (hex) ---")
    print(" ".join(f"{b:02X}" for b in program))
    print("\n--- Final CPU state ---")
    print(state)
