/*
  ==============================================================================

   This file is part of the JUCE framework examples.
   Copyright (c) Raw Material Software Limited

   The code included in this file is provided under the terms of the ISC license
   http://www.isc.org/downloads/software-support-policy/isc-license. Permission
   to use, copy, modify, and/or distribute this software for any purpose with or
   without fee is hereby granted provided that the above copyright notice and
   this permission notice appear in all copies.

   THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
   REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
   AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
   INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
   LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
   OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
   PERFORMANCE OF THIS SOFTWARE.

  ==============================================================================
*/

/*******************************************************************************
 The block below describes the properties of this PIP. A PIP is a short snippet
 of code that can be read by the Projucer and used to generate a JUCE project.

 BEGIN_JUCE_PIP_METADATA

 name:             FlangerPlugin
 version:          1.0.0
 vendor:           JUCE
 website:          oshe.io
 description:      Flanger audio plugin.

 dependencies:     juce_audio_basics, juce_audio_devices, juce_audio_formats,
                   juce_audio_plugin_client, juce_audio_processors,
                   juce_audio_utils, juce_core, juce_data_structures, juce_dsp,
                   juce_events, juce_graphics, juce_gui_basics, juce_gui_extra
 exporter:         Linux Makefile

 moduleFlags:      JUCE_STRICT_REFCOUNTEDPOINTER=1

 type:             AudioProcessor
 mainClass:        FlangerProcessor

 useLocalCopy:     1

 END_JUCE_PIP_METADATA

*******************************************************************************/

#pragma once


//==============================================================================
class FlangerProcessor final : public juce::AudioProcessor
{
public:

    //==============================================================================
    FlangerProcessor()
        : juce::AudioProcessor (BusesProperties().withInput  ("Input",  juce::AudioChannelSet::stereo())
                                                 .withOutput ("Output", juce::AudioChannelSet::stereo()))
    {
        addParameter (gain = new juce::AudioParameterFloat ({ "gain", 1 }, "Gain", 0.0f, 2.0f, 1.0f));
        addParameter (rate = new juce::AudioParameterFloat ({"rate", 1 }, "Rate", 0.0f, 10.0f, 0.2f)); // rate is in Hz
        addParameter (depth = new juce::AudioParameterFloat ({"depth", 1 }, "Depth", 0.0f, 1.0f, 0.9f));
        addParameter (delay = new juce::AudioParameterFloat ({ "delay", 1 }, "Delay", 0.001f, 0.01f, 0.003f)); // delay is in seconds
        addParameter (feedback = new juce::AudioParameterFloat ({ "feedback", 1 }, "Feedback", 0.0f, 1.0f, 0.1f));
        addParameter (mix = new juce::AudioParameterFloat ({ "mix", 1 }, "Mix", 0.0f, 1.0f, 0.3f));
        
        // Waveform 0: Pass-Through, Waveform 1: Sinusoidal LFO, Waveform 2: Saw Wave LFO, Waveform 3: Square Wave LFO
        addParameter (waveform = new juce::AudioParameterInt ({ "waveform", 1 }, "Waveform", 0, 3, 1));
        
        // Mode 0: Pass-Through, Mode 1: Additive Flanging, Mode 2: Subtractive Flanging, Mode 3: Through-Zero Flanging
        addParameter (flangMode = new juce::AudioParameterInt ({ "flangMode", 1 }, "Flanging Mode", 0, 3, 1));
    }

    //==============================================================================
    void prepareToPlay (double sampleRate, int samplesPerBlock) override
    {  
        // Sets specs for a JUCE DSP processor
        juce::dsp::ProcessSpec spec;
        spec.maximumBlockSize = samplesPerBlock;
        spec.sampleRate = sampleRate;
        spec.numChannels = getTotalNumOutputChannels();
        
        
        // Delay Lines
        
        // Initializes both delay lines
        chnl1delay.prepare (spec);
        chnl2delay.prepare (spec);
        
        // Since the delay parameter is limited to a maximum of 0.01s, and based on delayInSamples
        // which can double the value of the delay parameter based on the LFO, the maximum possible number of samples is sampleRate in samples/s * 0.02s
        chnl1delay.setMaximumDelayInSamples (sampleRate * 0.02f);
        chnl2delay.setMaximumDelayInSamples (sampleRate * 0.02f);
        
        // Converts delay in seconds to delay in samples and updates delay of both delay lines
        delayFloat = delay->get();
        chnl1delay.setDelay (delay->get() * sampleRate);
        chnl2delay.setDelay (delay->get() * sampleRate);
        
        
        // LFOs
        
        // Initializes all LFOs
        chnl1sineLFO.prepare (spec);
        chnl2sineLFO.prepare (spec);
        chnl1sawLFO.prepare (spec);
        chnl2sawLFO.prepare (spec);
        chnl1squareLFO.prepare (spec);
        chnl2squareLFO.prepare (spec);
        
        // Updates rate of all LFOs
        rateFloat = rate->get();
        chnl1sineLFO.setFrequency (rateFloat);
        chnl2sineLFO.setFrequency (rateFloat);
        chnl1sawLFO.setFrequency (rateFloat);
        chnl2sawLFO.setFrequency (rateFloat);
        chnl1squareLFO.setFrequency (rateFloat);
        chnl2squareLFO.setFrequency (rateFloat);
    }
    
    void releaseResources() override {}

    void processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&) override
    {
        gainFloat = gain->get();
        rateFloat = rate->get();
        depthFloat = depth->get();
        delayFloat = delay->get();
        feedbackFloat = feedback->get();
        mixFloat = mix->get();
        waveformInt = waveform->get();
        mode = flangMode->get();
        
        sampleRate = this->getSampleRate();
        totalNumInputChannels  = getTotalNumInputChannels();
        
        chnl1sineLFO.setFrequency (rateFloat);
        chnl2sineLFO.setFrequency (rateFloat);
        chnl1sawLFO.setFrequency (rateFloat);
        chnl2sawLFO.setFrequency (rateFloat);
        chnl1squareLFO.setFrequency (rateFloat);
        chnl2squareLFO.setFrequency (rateFloat);
        
        for (int channel = 0; channel < totalNumInputChannels; ++channel)
        {
            auto* channelData = buffer.getWritePointer (channel);
            
            switch(waveformInt)
            {
                case 1: // Sinusoidal LFO
                    switch(mode)
                    {
                        case 1: // Additive Flanging
                            if (channel == 0)
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl1sineLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl1delay.popSample(channel, delayInSamples, true);
                                    chnl1delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat); // Feedback
                            
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat); // Mix Delay (wet added to dry)
                                    channelData[sample] *= gainFloat; // Gain
                                }
                            }
                            else // Handles the second channel for stereo input but doesn't run for mono input
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl2sineLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl2delay.popSample(channel, delayInSamples, true);
                                    chnl2delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat);
                                    
                    
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat);
                                    channelData[sample] *= gainFloat;
                                }
                            }
                            break;
                    
                        case 2: // Subtractive Flanging
                            if (channel == 0)
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl1sineLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl1delay.popSample(channel, delayInSamples, true);
                                    chnl1delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat); // Feedback
                    
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) - (wetSample * mixFloat); // Mix Delay (wet subtracted from dry)
                                    channelData[sample] *= gainFloat; // Gain
                                }
                            }
                            else
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl2sineLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl2delay.popSample(channel, delayInSamples, true);
                                    chnl2delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat);
                    
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) - (wetSample * mixFloat);
                                    channelData[sample] *= gainFloat;
                                }
                            }
                            break;
                    
                        case 3: // Through-Zero Flanging
                            if (channel == 0)
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl1sineLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                            
                                    drySample = chnl1delay.popSample(channel, delayFloat * sampleRate, true); // Note: not actually dry since it's delayed but reusing the variable name for simplicity
                                    wetSample = chnl1delay.popSample(channel, delayInSamples, true);
                                    chnl1delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat); // Feedback
                            
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) - (wetSample * mixFloat); // Mix Delay (modulated wet added to delayed wet)
                                    channelData[sample] *= gainFloat; // Gain
                                }
                            }
                            else
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl2sineLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                            
                                    drySample = chnl2delay.popSample(channel, delayFloat * sampleRate, true);
                                    wetSample = chnl2delay.popSample(channel, delayInSamples, true);
                                    chnl2delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat);
                            
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) - (wetSample * mixFloat);
                                    channelData[sample] *= gainFloat;
                                }
                            }
                            break;
                    
                        default: // Pass-Through
                            break;
                    }
                    break;
                    
                case 2: // Saw Wave LFO
                    switch(mode)
                    {
                        case 1: // Additive Flanging
                            if (channel == 0)
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl1sawLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl1delay.popSample(channel, delayInSamples, true);
                                    chnl1delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat); // Feedback
                            
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat); // Mix Delay (wet added to dry)
                                    channelData[sample] *= gainFloat; // Gain
                                }
                            }
                            else // Handles the second channel for stereo input but doesn't run for mono input
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl2sawLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl2delay.popSample(channel, delayInSamples, true);
                                    chnl2delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat);
                    
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat);
                                    channelData[sample] *= gainFloat;
                                }
                            }
                            break;
                    
                        case 2: // Subtractive Flanging
                            if (channel == 0)
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl1sawLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl1delay.popSample(channel, delayInSamples, true);
                                    chnl1delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat); // Feedback
                    
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) - (wetSample * mixFloat); // Mix Delay (wet subtracted from dry)
                                    channelData[sample] *= gainFloat; // Gain
                                }
                            }
                            else
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl2sawLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl2delay.popSample(channel, delayInSamples, true);
                                    chnl2delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat);
                    
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) - (wetSample * mixFloat);
                                    channelData[sample] *= gainFloat;
                                }
                            }
                            break;
                    
                        case 3: // Through-Zero Flanging
                            if (channel == 0)
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl1sawLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                            
                                    drySample = chnl1delay.popSample(channel, delayFloat * sampleRate, true); // Note: not actually dry since it's delayed but reusing the variable name for simplicity
                                    wetSample = chnl1delay.popSample(channel, delayInSamples, true);
                                    chnl1delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat); // Feedback
                            
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat); // Mix Delay (modulated wet added to delayed wet)
                                    channelData[sample] *= gainFloat; // Gain
                                }
                            }
                            else
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl2sawLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                            
                                    drySample = chnl2delay.popSample(channel, delayFloat * sampleRate, true);
                                    wetSample = chnl2delay.popSample(channel, delayInSamples, true);
                                    chnl2delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat);
                            
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat);
                                    channelData[sample] *= gainFloat;
                                }
                            }
                            break;
                    
                        default: // Pass-Through
                            break;
                    }
                    break;
                    
                case 3: // Square Wave LFO
                    switch(mode)
                    {
                        case 1: // Additive Flanging
                            if (channel == 0)
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl1squareLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl1delay.popSample(channel, delayInSamples, true);
                                    chnl1delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat); // Feedback
                            
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat); // Mix Delay (wet added to dry)
                                    channelData[sample] *= gainFloat; // Gain
                                }
                            }
                            else // Handles the second channel for stereo input but doesn't run for mono input
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl2squareLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl2delay.popSample(channel, delayInSamples, true);
                                    chnl2delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat);
                    
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat);
                                    channelData[sample] *= gainFloat;
                                }
                            }
                            break;
                    
                        case 2: // Subtractive Flanging
                            if (channel == 0)
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl1squareLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl1delay.popSample(channel, delayInSamples, true);
                                    chnl1delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat); // Feedback
                    
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) - (wetSample * mixFloat); // Mix Delay (wet subtracted from dry)
                                    channelData[sample] *= gainFloat; // Gain
                                }
                            }
                            else
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl2squareLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                    
                                    drySample = channelData[sample];
                                    wetSample = chnl2delay.popSample(channel, delayInSamples, true);
                                    chnl2delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat);
                    
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) - (wetSample * mixFloat);
                                    channelData[sample] *= gainFloat;
                                }
                            }
                            break;
                    
                        case 3: // Through-Zero Flanging
                            if (channel == 0)
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl1squareLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                            
                                    drySample = chnl1delay.popSample(channel, delayFloat * sampleRate, true); // Note: not actually dry since it's delayed but reusing the variable name for simplicity
                                    wetSample = chnl1delay.popSample(channel, delayInSamples, true);
                                    chnl1delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat); // Feedback
                            
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat); // Mix Delay (modulated wet added to delayed wet)
                                    channelData[sample] *= gainFloat; // Gain
                                }
                            }
                            else
                            {
                                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                                {
                                    delayInSamples = (depthFloat * chnl2squareLFO.processSample(0.0f) * delayFloat + delayFloat) * sampleRate;
                            
                                    drySample = chnl2delay.popSample(channel, delayFloat * sampleRate, true);
                                    wetSample = chnl2delay.popSample(channel, delayInSamples, true);
                                    chnl2delay.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat);
                            
                                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat);
                                    channelData[sample] *= gainFloat;
                                }
                            }
                            break;
                    
                        default: // Pass-Through
                            break;
                    }
                    break;
                    
                default: // Pass-Through
                    break;
            }       
        }
    }

    //==============================================================================
    juce::AudioProcessorEditor* createEditor() override         { return new juce::GenericAudioProcessorEditor (*this); }
    bool hasEditor() const override                             { return true;   }

    //==============================================================================
    const juce::String getName() const override                 { return "Flanger PlugIn"; }
    bool acceptsMidi() const override                           { return false; }
    bool producesMidi() const override                          { return false; }
    double getTailLengthSeconds() const override                { return 0; }

    //==============================================================================
    int getNumPrograms() override                               { return 1; }
    int getCurrentProgram() override                            { return 0; }
    void setCurrentProgram (int) override                       {}
    const juce::String getProgramName (int) override            { return "None"; }
    void changeProgramName (int, const juce::String&) override  {}

    //==============================================================================
    void getStateInformation (juce::MemoryBlock& destData) override
    {
        juce::MemoryOutputStream (destData, true).writeFloat (*gain);
        juce::MemoryOutputStream (destData, true).writeFloat (*rate);
        juce::MemoryOutputStream (destData, true).writeFloat (*depth);
        juce::MemoryOutputStream (destData, true).writeFloat (*delay);
        juce::MemoryOutputStream (destData, true).writeFloat (*feedback);
        juce::MemoryOutputStream (destData, true).writeFloat (*mix);
        juce::MemoryOutputStream (destData, true).writeInt (*waveform);
        juce::MemoryOutputStream (destData, true).writeInt (*flangMode);
    }

    void setStateInformation (const void* data, int sizeInBytes) override
    {
        gain->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        rate->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        depth->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        delay->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        feedback->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        mix->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        waveform->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readInt());
        flangMode->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readInt());
    }

    //==============================================================================
    bool isBusesLayoutSupported (const BusesLayout& layouts) const override
    {
        const auto& mainInLayout  = layouts.getChannelSet (true,  0);
        const auto& mainOutLayout = layouts.getChannelSet (false, 0);

        return (mainInLayout == mainOutLayout && (! mainInLayout.isDisabled()));
    }

private:
    //==============================================================================
    juce::AudioParameterFloat* gain;
    juce::AudioParameterFloat* rate;
    juce::AudioParameterFloat* depth;
    juce::AudioParameterFloat* delay;
    juce::AudioParameterFloat* feedback;
    juce::AudioParameterFloat* mix;
    juce::AudioParameterInt* waveform;
    juce::AudioParameterInt* flangMode;
    
    float gainFloat;
    float rateFloat;
    float depthFloat;
    float delayFloat;
    float feedbackFloat;
    float mixFloat;
    int waveformInt;
    int mode;
    
    float drySample;
    float wetSample;
    double sampleRate;
    int totalNumInputChannels;
    int delayInSamples;
    
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Thiran> chnl1delay;
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Thiran> chnl2delay;
    
    // The last argument for the following lines is the number of points in the lookup table
    juce::dsp::Oscillator<float> chnl1sineLFO { [](float x) { return std::sin (x); }, 500 }; // Sine Wave
    juce::dsp::Oscillator<float> chnl1sawLFO { [](float x) { return x / juce::MathConstants<float>::pi; }, 10000 }; // Saw Wave
    juce::dsp::Oscillator<float> chnl1squareLFO { [](float x) { return x < 0.0f ? -1.0f : 1.0f; }, 10000 }; // Square Wave
    juce::dsp::Oscillator<float> chnl2sineLFO { [](float x) { return std::sin (x); }, 500 }; // Sine Wave
    juce::dsp::Oscillator<float> chnl2sawLFO { [](float x) { return x / juce::MathConstants<float>::pi; }, 10000 }; // Saw Wave
    juce::dsp::Oscillator<float> chnl2squareLFO { [](float x) { return x < 0.0f ? -1.0f : 1.0f; }, 10000 }; // Square Wave
    
    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (FlangerProcessor)
};
