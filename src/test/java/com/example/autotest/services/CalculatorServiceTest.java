package com.example.autotest.services;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

@ExtendWith(MockitoExtension.class)
public class CalculatorServiceTest {

    @InjectMocks
    private CalculatorService calculatorService;

    @Test
    @DisplayName("add two positive numbers")
    public void addTwoPositiveNumbers() {
        int result = calculatorService.add(5, 7);
        assertEquals(12, result);
    }

    @Test
    @DisplayName("add two negative numbers")
    public void addTwoNegativeNumbers() {
        int result = calculatorService.add(-5, -7);
        assertEquals(-12, result);
    }

    @Test
    @DisplayName("add one positive and one negative number")
    public void addOnePositiveAndOneNegativeNumber() {
        int result = calculatorService.add(5, -7);
        assertEquals(-2, result);
    }

    @Test
    @DisplayName("divide two positive numbers")
    public void divideTwoPositiveNumbers() {
        int result = calculatorService.divide(10, 2);
        assertEquals(5, result);
    }

    @Test
    @DisplayName("divide two negative numbers")
    public void divideTwoNegativeNumbers() {
        int result = calculatorService.divide(-10, -2);
        assertEquals(5, result);
    }

    @Test
    @DisplayName("divide one positive and one negative number")
    public void divideOnePositiveAndOneNegativeNumber() {
        int result = calculatorService.divide(10, -2);
        assertEquals(-5, result);
    }

    @Test
    @DisplayName("divide by zero")
    public void divideByZero() {
        RuntimeException exception = assertThrows(RuntimeException.class, () -> calculatorService.divide(10, 0));
        assertEquals("Cannot divide by zero", exception.getMessage());
    }
}