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
<<<<<<< HEAD

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
=======

    @Test
    @DisplayName("testAddHappyPath")
    public void testAddHappyPath() throws Exception {
        when(service.add(1, 2)).thenReturn(3);
        mockMvc.perform(get("/calc/add")
                .param("a", "1")
                .param("b", "2"))
                .andExpect(status().isOk())
                .andExpect(content().string("3"));
>>>>>>> 987c234e46e6be95a78a2fc9ee37172a25bbfa38
    }

    @Test
    @DisplayName("testAddNegativeNumbers")
<<<<<<< HEAD
    void testAddNegativeNumbers() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "-5")
                .param("b", "-5"))
                .andExpect(status().isOk())
                .andExpect(content().string("10"));
        verify(service, times(1)).add(-5, -5);
=======
    public void testAddNegativeNumbers() throws Exception {
        when(service.add(-1, -2)).thenReturn(-3);
        mockMvc.perform(get("/calc/add")
                .param("a", "-1")
                .param("b", "-2"))
                .andExpect(status().isOk())
                .andExpect(content().string("-3"));
>>>>>>> 987c234e46e6be95a78a2fc9ee37172a25bbfa38
    }

    @Test
    @DisplayName("testAddMissingParameters")
<<<<<<< HEAD
    void testAddMissingParameters() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "5"))
=======
    public void testAddMissingParameters() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "1"))
>>>>>>> 987c234e46e6be95a78a2fc9ee37172a25bbfa38
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("testAddNonIntegerParameters")
<<<<<<< HEAD
    void testAddNonIntegerParameters() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "five")
                .param("b", "5"))
=======
    public void testAddNonIntegerParameters() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "one")
                .param("b", "2"))
>>>>>>> 987c234e46e6be95a78a2fc9ee37172a25bbfa38
                .andExpect(status().isBadRequest());
    }
}