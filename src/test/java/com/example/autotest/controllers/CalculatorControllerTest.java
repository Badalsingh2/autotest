package com.example.autotest.controllers;

import com.example.autotest.services.CalculatorService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.MockBean;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.result.MockMvcResultMatchers;

import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.when;

@WebMvcTest(CalculatorController.class)
public class CalculatorControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private CalculatorService calculatorService;

    @BeforeEach
    void setup() {
        when(calculatorService.add(anyInt(), anyInt())).thenReturn(10);
    }

    @Test
    @DisplayName("testAddHappyPath")
    void testAddHappyPath() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get("/calc/add")
                .param("a", "5")
                .param("b", "5"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.content().string("10"));
    }

    @Test
    @DisplayName("testAddNegativeNumbers")
    void testAddNegativeNumbers() throws Exception {
        when(calculatorService.add(-5, -5)).thenReturn(-10);
        mockMvc.perform(MockMvcRequestBuilders.get("/calc/add")
                .param("a", "-5")
                .param("b", "-5"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.content().string("-10"));
    }

    @Test
    @DisplayName("testAddMissingParameterA")
    void testAddMissingParameterA() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get("/calc/add")
                .param("b", "5"))
                .andExpect(MockMvcResultMatchers.status().isBadRequest());
    }

    @Test
    @DisplayName("testAddMissingParameterB")
    void testAddMissingParameterB() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get("/calc/add")
                .param("a", "5"))
                .andExpect(MockMvcResultMatchers.status().isBadRequest());
    }

    @Test
    @DisplayName("testAddNonIntegerParameterA")
    void testAddNonIntegerParameterA() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get("/calc/add")
                .param("a", "abc")
                .param("b", "5"))
                .andExpect(MockMvcResultMatchers.status().isBadRequest());
    }

    @Test
    @DisplayName("testAddNonIntegerParameterB")
    void testAddNonIntegerParameterB() throws Exception {
        mockMvc.perform(MockMvcRequestBuilders.get("/calc/add")
                .param("a", "5")
                .param("b", "abc"))
                .andExpect(MockMvcResultMatchers.status().isBadRequest());
    }
}