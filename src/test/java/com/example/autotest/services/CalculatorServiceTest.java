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
    private Object dependency; // no dependencies in CalculatorService, but added for completeness

    @BeforeEach
    void setup() {
        // no setup needed for this test
    }

    @Test
    @DisplayName("testAddHappyPath")
    void testAddHappyPath() {
        int result = calculatorService.add(2, 3);
        assertEquals(5, result);
    }

    @Test
    @DisplayName("testAddNegativeNumbers")
    void testAddNegativeNumbers() {
        int result = calculatorService.add(-2, -3);
        assertEquals(-5, result);
    }

    @Test
    @DisplayName("testAddMixedNumbers")
    void testAddMixedNumbers() {
        int result = calculatorService.add(-2, 3);
        assertEquals(1, result);
    }

    @Test
    @DisplayName("testDivideHappyPath")
    void testDivideHappyPath() {
        int result = calculatorService.divide(6, 2);
        assertEquals(3, result);
    }

    @Test
    @DisplayName("testDivideByOne")
    void testDivideByOne() {
        int result = calculatorService.divide(6, 1);
        assertEquals(6, result);
    }

    @Test
    @DisplayName("testDivideNegativeNumbers")
    void testDivideNegativeNumbers() {
        int result = calculatorService.divide(-6, -2);
        assertEquals(3, result);
    }

    @Test
    @DisplayName("testDivideByZero")
    void testDivideByZero() {
        assertThrows(RuntimeException.class, () -> calculatorService.divide(6, 0));
    }
}