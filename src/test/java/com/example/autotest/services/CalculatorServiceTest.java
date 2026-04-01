package com.example.autotest.services;

import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.Mock;
import org.mockito.InjectMocks;
import static org.mockito.Mockito.*;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@ExtendWith(MockitoExtension.class)
public class CalculatorServiceTest {

    @Mock
    private Object dependency; // no dependencies in CalculatorService, but added for completeness

    @InjectMocks
    private CalculatorService calculatorService;

<<<<<<< HEAD
    @BeforeEach
    public void setup() {
        // no setup needed for this test
=======
    @Mock
    private Object dependency; // no dependencies in CalculatorService, but added for demonstration

    @BeforeEach
    public void setup() {
        // no setup needed for this simple service
>>>>>>> 987c234e46e6be95a78a2fc9ee37172a25bbfa38
    }

    @Test
    @DisplayName("testAddHappyPath")
    public void testAddHappyPath() {
        int result = calculatorService.add(2, 3);
        assertEquals(5, result);
    }

    @Test
    @DisplayName("testAddNegativeNumbers")
    public void testAddNegativeNumbers() {
        int result = calculatorService.add(-2, -3);
        assertEquals(-5, result);
    }

    @Test
    @DisplayName("testAddMixedNumbers")
    public void testAddMixedNumbers() {
        int result = calculatorService.add(-2, 3);
        assertEquals(1, result);
    }

    @Test
    @DisplayName("testDivideHappyPath")
    public void testDivideHappyPath() {
        int result = calculatorService.divide(6, 2);
        assertEquals(3, result);
    }

    @Test
<<<<<<< HEAD
    @DisplayName("testDivideByZero")
    public void testDivideByZero() {
        RuntimeException exception = assertThrows(RuntimeException.class, () -> calculatorService.divide(6, 0));
        assertEquals("Cannot divide by zero", exception.getMessage());
=======
    @DisplayName("testDivideByOne")
    public void testDivideByOne() {
        int result = calculatorService.divide(6, 1);
        assertEquals(6, result);
>>>>>>> 987c234e46e6be95a78a2fc9ee37172a25bbfa38
    }

    @Test
    @DisplayName("testDivideNegativeNumbers")
    public void testDivideNegativeNumbers() {
        int result = calculatorService.divide(-6, -2);
        assertEquals(3, result);
    }

    @Test
    @DisplayName("testDivideMixedNumbers")
    public void testDivideMixedNumbers() {
        int result = calculatorService.divide(-6, 2);
        assertEquals(-3, result);
<<<<<<< HEAD
=======
    }

    @Test
    @DisplayName("testDivideByZero")
    public void testDivideByZero() {
        assertThrows(RuntimeException.class, () -> calculatorService.divide(6, 0));
>>>>>>> 987c234e46e6be95a78a2fc9ee37172a25bbfa38
    }
}