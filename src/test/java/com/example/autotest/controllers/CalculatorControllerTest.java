package com.example.autotest.controllers;
import org.junit.jupiter.api.Assertions;

import com.example.autotest.services.CalculatorService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.result.MockMvcResultMatchers;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

@WebMvcTest(CalculatorController.class)
public class CalculatorControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private CalculatorService service;

    @BeforeEach
    void setup() {
        when(service.add(anyInt(), anyInt())).thenReturn(10);
    }

    @Test
    @DisplayName("testAddHappyPath")
    void testAddHappyPath() throws Exception {
        when(service.add(5, 5)).thenReturn(10);
        mockMvc.perform(get("/calc/add")
                .param("a", "5")
                .param("b", "5"))
                .andExpect(status().isOk())
                .andExpect(content().string("10"));
    }

    @Test
    @DisplayName("testAddNegativeNumbers")
    void testAddNegativeNumbers() throws Exception {
        when(service.add(-5, -5)).thenReturn(-10);
        mockMvc.perform(get("/calc/add")
                .param("a", "-5")
                .param("b", "-5"))
                .andExpect(status().isOk())
                .andExpect(content().string("-10"));
    }

    @Test
    @DisplayName("testAddLargeNumbers")
    void testAddLargeNumbers() throws Exception {
        when(service.add(1000, 1000)).thenReturn(2000);
        mockMvc.perform(get("/calc/add")
                .param("a", "1000")
                .param("b", "1000"))
                .andExpect(status().isOk())
                .andExpect(content().string("2000"));
    }

    @Test
    @DisplayName("testAddMissingParameters")
    void testAddMissingParameters() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "5"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("testAddInvalidParameters")
    void testAddInvalidParameters() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "abc")
                .param("b", "5"))
                .andExpect(status().isBadRequest());
    }
}