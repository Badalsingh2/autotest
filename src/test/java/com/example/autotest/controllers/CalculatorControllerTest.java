package com.example.autotest.controllers;

import com.example.autotest.services.CalculatorService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

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
        mockMvc.perform(get("/calc/add")
                .param("a", "5")
                .param("b", "5"))
                .andExpect(status().isOk())
                .andExpect(content().string("10"));
        verify(service, times(1)).add(5, 5);
    }

    @Test
    @DisplayName("testAddNegativeNumbers")
    void testAddNegativeNumbers() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "-5")
                .param("b", "-5"))
                .andExpect(status().isOk())
                .andExpect(content().string("10"));
        verify(service, times(1)).add(-5, -5);
    }

    @Test
    @DisplayName("testAddMissingParameters")
    void testAddMissingParameters() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "5"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("testAddNonIntegerParameters")
    void testAddNonIntegerParameters() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "five")
                .param("b", "5"))
                .andExpect(status().isBadRequest());
    }
}