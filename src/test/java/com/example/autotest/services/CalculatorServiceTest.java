package com.example.autotest.services;
import org.junit.jupiter.api.Assertions;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;
import org.mockito.Mock;
import org.mockito.InjectMocks;
import static org.mockito.Mockito.*;
import static org.junit.jupiter.api.Assertions.*;

@ExtendWith(MockitoExtension.class)
public class CalculatorServiceTest {

    @Mock
    private CalculatorService calculatorServiceMock;

    @InjectMocks
    private CalculatorService calculatorService;

    @BeforeEach
    void setup() {
        calculatorService = new CalculatorService();
    }

    @Test
    @DisplayName("testAddHappyPath")
    void testAddHappyPath() {
        int result = calculatorService.add(5, 7);
        assertEquals(12, result);
    }

    @Test
    @DisplayName("testAddNegativeNumbers")
    void testAddNegativeNumbers() {
        int result = calculatorService.add(-5, -7);
        assertEquals(-12, result);
    }

    @Test
    @DisplayName("testAddMixedNumbers")
    void testAddMixedNumbers() {
        int result = calculatorService.add(-5, 7);
        assertEquals(2, result);
    }

    @Test
    @DisplayName("testDivideHappyPath")
    void testDivideHappyPath() {
        int result = calculatorService.divide(10, 2);
        assertEquals(5, result);
    }

    @Test
    @DisplayName("testDivideByZero")
    void testDivideByZero() {
        assertThrows(RuntimeException.class, () -> calculatorService.divide(10, 0));
    }

    @Test
    @DisplayName("testDivideNegativeNumbers")
    void testDivideNegativeNumbers() {
        int result = calculatorService.divide(-10, 2);
        assertEquals(-5, result);
    }

    @Test
    @DisplayName("testDivideMixedNumbers")
    void testDivideMixedNumbers() {
        int result = calculatorService.divide(-10, -2);
        assertEquals(5, result);
    }
}