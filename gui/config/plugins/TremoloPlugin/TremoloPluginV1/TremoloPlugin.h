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
 vendor:           JUCE
 website:          http://juce.com
 description:      Tremolo audio plugin.

 dependencies:     juce_audio_basics, juce_audio_devices, juce_audio_formats,
                   juce_audio_plugin_client, juce_audio_processors,
                   juce_audio_utils, juce_core, juce_data_structures,
                   juce_events, juce_graphics, juce_gui_basics, juce_gui_extra
 exporters:        xcode_mac, vs2022

 moduleFlags:      JUCE_STRICT_REFCOUNTEDPOINTER=1

 type:             AudioProcessor
 mainClass:        TremoloProcessor

 useLocalCopy:     1

 END_JUCE_PIP_METADATA

*******************************************************************************/

#pragma once


//==============================================================================
class TremoloProcessor final : public AudioProcessor
{
public:

    //==============================================================================
    TremoloProcessor()
        : AudioProcessor (BusesProperties().withInput  ("Input",  AudioChannelSet::stereo())
                                           .withOutput ("Output", AudioChannelSet::stereo()))
    {
        addParameter (rate = new AudioParameterFloat ({"rate", 1}, "Rate", 0.0f, 20.0f, 10.0f)); // rate is in Hz
        addParameter (depth = new AudioParameterFloat ({"depth", 1}, "Depth", 0.0f, 1.0f, 0.5f));
        addParameter (gain = new AudioParameterFloat ({"gain", 1}, "Gain", 0.0f, 2.0f, 1.0f));
    }

    //==============================================================================
    void prepareToPlay (double, int) override
    {  
        position = 0; // Initial value for position within LFO signal
    }
    
    void releaseResources() override {}

    void processBlock (AudioBuffer<float>& buffer, MidiBuffer&) override
    {  
        rateFloat = rate->get();
        depthFloat = depth->get();
        gainFloat = gain->get();
        
        sampleRate = this->getSampleRate();
        totalNumInputChannels  = getTotalNumInputChannels();
        
        w = 6.28318530718 * rateFloat;
        LFO = sin(position * w);
    
        for (int channel = 0; channel < totalNumInputChannels; ++channel)
        {
            auto* channelData = buffer.getWritePointer (channel);

            for (int i = 0; i < buffer.getNumSamples(); ++i)
            {    
                channelData[i] = channelData[i] * (depthFloat * LFO + (1.0f - depthFloat)); // Tremolo
                channelData[i] *= gainFloat; // Gain
                
                position += (1 / sampleRate); // Increment position by sampling interval
                if (position >= (1 / rateFloat)) // Check if position is beyond one LFO period
                {
                    position = 0;
                }
            }
        }
    }

    void processBlock (AudioBuffer<double>& buffer, MidiBuffer&) override
    {
        rateFloat = rate->get();
        depthFloat = depth->get();
        gainFloat = gain->get();
        
        sampleRate = this->getSampleRate();
        totalNumInputChannels  = getTotalNumInputChannels();
        
        w = 6.28318530718 * rateFloat;
        LFO = sin(position * w);
    
        for (int channel = 0; channel < totalNumInputChannels; ++channel)
        {
            auto* channelData = buffer.getWritePointer (channel);

            for (int i = 0; i < buffer.getNumSamples(); ++i)
            {    
                channelData[i] = channelData[i] * (depthFloat * LFO + (1.0f - depthFloat)); // Tremolo
                channelData[i] *= gainFloat; // Gain
                
                position += (1 / sampleRate); // Increment position by sampling interval
                if (position >= (1 / rateFloat)) // Check if position is beyond one LFO period
                {
                    position = 0;
                }
            }
        }
    }

    //==============================================================================
    AudioProcessorEditor* createEditor() override          { return new GenericAudioProcessorEditor (*this); }
    bool hasEditor() const override                        { return true;   }

    //==============================================================================
    const String getName() const override                  { return "Tremolo Plugin"; }
    bool acceptsMidi() const override                      { return false; }
    bool producesMidi() const override                     { return false; }
    double getTailLengthSeconds() const override           { return 0; }

    //==============================================================================
    int getNumPrograms() override                          { return 1; }
    int getCurrentProgram() override                       { return 0; }
    void setCurrentProgram (int) override                  {}
    const String getProgramName (int) override             { return "None"; }
    void changeProgramName (int, const String&) override   {}

    //==============================================================================
    void getStateInformation (MemoryBlock& destData) override
    {
        MemoryOutputStream (destData, true).writeFloat (*rate);
        MemoryOutputStream (destData, true).writeFloat (*depth);
        MemoryOutputStream (destData, true).writeFloat (*gain);
    }

    void setStateInformation (const void* data, int sizeInBytes) override
    {
        rate->setValueNotifyingHost (MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        depth->setValueNotifyingHost (MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        gain->setValueNotifyingHost (MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
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
    AudioParameterFloat* rate;
    AudioParameterFloat* depth;
    AudioParameterFloat* gain;
    
    float rateFloat;
    float depthFloat;
    float gainFloat;
    
    double sampleRate;
    int totalNumInputChannels;
    float position; // Current position within LFO signal
    float w; // w is in radians per second
    float LFO; // Low-frequency oscillator

    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (TremoloProcessor)
};
