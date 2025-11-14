from demo_program import assemble_and_run_demo, DEMO_ASM, LOAD_TEST

# -----------------------------
#  Безадресная/Гарвард/Сумма элементов
# -----------------------------

if __name__ == "__main__":
    program, state = assemble_and_run_demo([0, 5, -2, 112, 7], trace=True,program=DEMO_ASM)
    # program, state = assemble_and_run_demo([1, -2, 112, 7, 0], trace=True,program=LOAD_TEST)

    print("\n--- Machine code (hex) ---")
    print(" ".join(f"{b:02X}" for b in program))
    print("\n--- Final CPU state ---")
    print(state)
