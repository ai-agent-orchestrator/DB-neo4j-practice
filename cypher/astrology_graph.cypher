// All 12 signs and their shared traits. Browser: choose Graph after execution.
MATCH p = (z:ZodiacSign)-[:HAS_TRAIT]->(:SharedTrait)
RETURN p;
