package com.example.autotest.controllers;

import com.example.autotest.services.CalculatorService;
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

    @Test
    @DisplayName("testAddHappyPath")
    public void testAddHappyPath() throws Exception {
        when(service.add(anyInt(), anyInt())).thenReturn(5);
        mockMvc.perform(get("/calc/add")
                .param("a", "2")
                .param("b", "3"))
                .andExpect(status().isOk())
                .andExpect(content().string("5"));
    }

    @Test
    @DisplayName("testAddNegativeNumbers")
    public void testAddNegativeNumbers() throws Exception {
        when(service.add(anyInt(), anyInt())).thenReturn(-5);
        mockMvc.perform(get("/calc/add")
                .param("a", "-2")
                .param("b", "-3"))
                .andExpect(status().isOk())
                .andExpect(content().string("-5"));
    }

    @Test
    @DisplayName("testAddMissingParameterA")
    public void testAddMissingParameterA() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("b", "3"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("testAddMissingParameterB")
    public void testAddMissingParameterB() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "2"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("testAddNonIntegerParameterA")
    public void testAddNonIntegerParameterA() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "abc")
                .param("b", "3"))
                .andExpect(status().isBadRequest());
    }

    @Test
    @DisplayName("testAddNonIntegerParameterB")
    public void testAddNonIntegerParameterB() throws Exception {
        mockMvc.perform(get("/calc/add")
                .param("a", "2")
                .param("b", "abc"))
                .andExpect(status().isBadRequest());
    }
}