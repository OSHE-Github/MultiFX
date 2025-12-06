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

 name:             TremoloPlugin
 version:          1.0.0
 website:          oshe.io
 description:      Tremolo audio plugin.

 dependencies:     juce_audio_basics, juce_audio_devices, juce_audio_formats,
                   juce_audio_plugin_client, juce_audio_processors,
                   juce_audio_utils, juce_core, juce_data_structures, juce_dsp,
                   juce_events, juce_graphics, juce_gui_basics, juce_gui_extra
 exporter:         Linux Makefile

 moduleFlags:      JUCE_STRICT_REFCOUNTEDPOINTER=1

 type:             AudioProcessor
 mainClass:        TremoloProcessor

 useLocalCopy:     1

 END_JUCE_PIP_METADATA

*******************************************************************************/

#pragma once


//==============================================================================
class TremoloProcessor final : public juce::AudioProcessor
{
public:

    //==============================================================================
    TremoloProcessor()
        : juce::AudioProcessor (BusesProperties().withInput  ("Input",  juce::AudioChannelSet::stereo())
                                                 .withOutput ("Output", juce::AudioChannelSet::stereo()))
    {
        addParameter (rate = new juce::AudioParameterFloat ({"rate", 1}, "Rate", 0.0f, 20.0f, 2.0f)); // rate is in Hz
        addParameter (depth = new juce::AudioParameterFloat ({"depth", 1}, "Depth", 0.0f, 1.0f, 0.2f));
        addParameter (gain = new juce::AudioParameterFloat ({"gain", 1}, "Gain", 0.0f, 2.0f, 1.0f));
        
        // Waveform 0: Pass-Through, Waveform 1: Sinusoidal LFO, Waveform 2: Saw Wave LFO, Waveform 3: Square Wave LFO
        addParameter (waveform = new juce::AudioParameterInt ({ "waveform", 1 }, "Waveform", 0, 3, 1));
    }

    //==============================================================================
    void prepareToPlay (double sampleRate, int samplesPerBlock) override
    {
        // Same ProcessSpec used for all LFOs
        juce::dsp::ProcessSpec spec;
        spec.maximumBlockSize = samplesPerBlock;
        spec.sampleRate = sampleRate;
        spec.numChannels = getTotalNumOutputChannels();
        
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
        rateFloat = rate->get();
        depthFloat = depth->get();
        gainFloat = gain->get();
        waveformInt = waveform->get();
        
        totalNumInputChannels = getTotalNumInputChannels();
        
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
                    // Both channels have their own LFO for stereo input
                    if (channel == 0)
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            // Tremolo and gain applied to audio sample
                            channelData[sample] = (channelData[sample] * (depthFloat * chnl1sineLFO.processSample(0.0f) + (1.0f - depthFloat))) * gainFloat;
                        }
                    }
                    else // Handles the second channel for stereo input but doesn't run for mono input
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            channelData[sample] = (channelData[sample] * (depthFloat * chnl2sineLFO.processSample(0.0f) + (1.0f - depthFloat))) * gainFloat;
                        }
                    }
                    break;
                    
                case 2: // Saw Wave LFO
                    if (channel == 0)
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            channelData[sample] = (channelData[sample] * (depthFloat * chnl1sawLFO.processSample(0.0f) + (1.0f - depthFloat))) * gainFloat;
                        }
                    }
                    else
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            channelData[sample] = (channelData[sample] * (depthFloat * chnl2sawLFO.processSample(0.0f) + (1.0f - depthFloat))) * gainFloat;
                        }
                    }
                    break;
                    
                case 3: // Square Wave LFO
                    if (channel == 0)
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            channelData[sample] = (channelData[sample] * (depthFloat * chnl1squareLFO.processSample(0.0f) + (1.0f - depthFloat))) * gainFloat;
                        }
                    }
                    else
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            channelData[sample] = (channelData[sample] * (depthFloat * chnl2squareLFO.processSample(0.0f) + (1.0f - depthFloat))) * gainFloat;
                        }
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
    const juce::String getName() const override                 { return "Tremolo PlugIn"; }
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
        juce::MemoryOutputStream (destData, true).writeFloat (*rate);
        juce::MemoryOutputStream (destData, true).writeFloat (*depth);
        juce::MemoryOutputStream (destData, true).writeFloat (*gain);
        juce::MemoryOutputStream (destData, true).writeInt (*waveform);
    }

    void setStateInformation (const void* data, int sizeInBytes) override
    {
        rate->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        depth->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        gain->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        waveform->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readInt());
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
    juce::AudioParameterFloat* rate;
    juce::AudioParameterFloat* depth;
    juce::AudioParameterFloat* gain;
    juce::AudioParameterInt* waveform;
    
    float rateFloat;
    float depthFloat;
    float gainFloat;
    int waveformInt;
    
    int totalNumInputChannels;
    
    // The last argument for the following lines is the number of points in the lookup table
    juce::dsp::Oscillator<float> chnl1sineLFO { [](float x) { return std::sin (x); }, 500 }; // Sine Wave
    juce::dsp::Oscillator<float> chnl1sawLFO { [](float x) { return x / juce::MathConstants<float>::pi; }, 10000 }; // Saw Wave
    juce::dsp::Oscillator<float> chnl1squareLFO { [](float x) { return x < 0.0f ? -1.0f : 1.0f; }, 10000 }; // Square Wave
    juce::dsp::Oscillator<float> chnl2sineLFO { [](float x) { return std::sin (x); }, 500 }; // Sine Wave
    juce::dsp::Oscillator<float> chnl2sawLFO { [](float x) { return x / juce::MathConstants<float>::pi; }, 10000 }; // Saw Wave
    juce::dsp::Oscillator<float> chnl2squareLFO { [](float x) { return x < 0.0f ? -1.0f : 1.0f; }, 10000 }; // Square Wave

    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TremoloProcessor)
};
