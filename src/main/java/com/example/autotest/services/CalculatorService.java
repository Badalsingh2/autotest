package com.example.autotest.services;

import org.springframework.stereotype.Service;

@Service
public class CalculatorService {

    public int add(int a, int b) {
        return a + b;
    }

    public int divide(int a, int b) {
        if (b == 0) throw new RuntimeException("Cannot divide by zero");
        return a / b;
    }
}