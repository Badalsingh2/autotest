package com.example.autotest.controllers;

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

@WebMvcTest(CalculatorController.class)
public class CalculatorControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private CalculatorService calculatorService;

    @Test
    @DisplayName("testAddHappyPath")
    public void testAddHappyPath() throws Exception {
        when(calculatorService.add(2, 3)).thenReturn(5);
        mockMvc.perform(get("/calc/add").param("a", "2").param("b", "3"))
                .andExpect(status().isOk())
                .andExpect(content().string("5"));
        verify(calculatorService, times(1)).add(2, 3);
    }

    @Test
    @DisplayName("testAddNegativeNumbers")
    public void testAddNegativeNumbers() throws Exception {
        when(calculatorService.add(-2, -3)).thenReturn(-5);
        mockMvc.perform(get("/calc/add").param("a", "-2").param("b", "-3"))
                .andExpect(status().isOk())
                .andExpect(content().string("-5"));
        verify(calculatorService, times(1)).add(-2, -3);
    }

    @Test
    @DisplayName("testAddMissingParameters")
    public void testAddMissingParameters() throws Exception {
        mockMvc.perform(get("/calc/add").param("a", "2"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("testAddNonIntegerParameters")
    public void testAddNonIntegerParameters() throws Exception {
        mockMvc.perform(get("/calc/add").param("a", "two").param("b", "3"))
                .andExpect(status().isBadRequest());
    }
}