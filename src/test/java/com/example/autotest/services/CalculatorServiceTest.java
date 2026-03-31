package com.example.autotest.services;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.Mock;
import org.mockito.InjectMocks;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
public class CalculatorServiceTest {

    @InjectMocks
    private CalculatorService calculatorService;

    @Mock
    private Object dependency; // no dependencies in CalculatorService, but added for demonstration

    @BeforeEach
    public void setup() {
        // no setup needed for this simple service
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
    @DisplayName("testDivideByOne")
    public void testDivideByOne() {
        int result = calculatorService.divide(6, 1);
        assertEquals(6, result);
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
    }

    @Test
    @DisplayName("testDivideByZero")
    public void testDivideByZero() {
        assertThrows(RuntimeException.class, () -> calculatorService.divide(6, 0));
    }
}