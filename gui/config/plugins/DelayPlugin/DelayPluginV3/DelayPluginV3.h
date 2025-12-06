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

 name:             DelayPlugin
 version:          1.0.0
 vendor:           JUCE
 website:          oshe.io
 description:      Delay audio plugin.

 dependencies:     juce_audio_basics, juce_audio_devices, juce_audio_formats,
                   juce_audio_plugin_client, juce_audio_processors,
                   juce_audio_utils, juce_core, juce_data_structures, juce_dsp,
                   juce_events, juce_graphics, juce_gui_basics, juce_gui_extra
 exporters:        xcode_mac, vs2022

 moduleFlags:      JUCE_STRICT_REFCOUNTEDPOINTER=1

 type:             AudioProcessor
 mainClass:        DelayProcessor

 useLocalCopy:     1

 END_JUCE_PIP_METADATA

*******************************************************************************/

#pragma once


//==============================================================================
class DelayProcessor final : public juce::AudioProcessor
{
public:

    //==============================================================================
    DelayProcessor()
        : juce::AudioProcessor (BusesProperties().withInput  ("Input",  juce::AudioChannelSet::stereo())
                                                 .withOutput ("Output", juce::AudioChannelSet::stereo()))
    {
        addParameter (gain = new juce::AudioParameterFloat ({ "gain", 1 }, "Gain", 0.0f, 1.0f, 0.5f));
        addParameter (delay = new juce::AudioParameterFloat ({ "delay", 1 }, "Delay", 0.001f, 1.0f, 0.1f)); // Delay is in seconds
        addParameter (feedback = new juce::AudioParameterFloat ({ "feedback", 1 }, "Feedback", 0.0f, 1.0f, 0.2f));
        addParameter (mix = new juce::AudioParameterFloat ({ "mix", 1 }, "Mix", 0.0f, 1.0f, 0.5f));
    }

    //==============================================================================
    void prepareToPlay (double sampleRate, int samplesPerBlock) override
    {
        // Sets specs for a JUCE DSP processor
        juce::dsp::ProcessSpec spec;
        spec.maximumBlockSize = samplesPerBlock;
        spec.sampleRate = sampleRate;
        spec.numChannels = getTotalNumOutputChannels();
        
        // Initializes delay line processors
        delayCHNL1.prepare (spec);
        delayCHNL2.prepare (spec);
        
        // Since the delay parameter is limited to a maximum of 1s, the maximum possible delay in samples is sampleRate in samples/s * 1s
        delayCHNL1.setMaximumDelayInSamples (sampleRate);
        delayCHNL2.setMaximumDelayInSamples (sampleRate);
        
        // Delay in seconds is converted to delay in samples
        delayFloat = delay->get();
        delayCHNL1.setDelay (delayFloat * sampleRate);
        delayCHNL2.setDelay (delayFloat * sampleRate);
    }
    
    void releaseResources() override {}

    void processBlock (juce::AudioBuffer<float>& buffer, juce::MidiBuffer&) override
    {
        gainFloat = gain->get();
        delayFloat = delay->get();
        feedbackFloat = feedback->get();
        mixFloat = mix->get();
        
        sampleRate = this->getSampleRate();
        totalNumInputChannels  = getTotalNumInputChannels();
        
        delayCHNL1.setDelay (delayFloat * sampleRate);
        delayCHNL2.setDelay (delayFloat * sampleRate);
        
        for (int channel = 0; channel < totalNumInputChannels; ++channel)
        {
            auto* channelData = buffer.getWritePointer (channel);
            
            if (channel == 0)
            {
                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                {
                    drySample = channelData[sample];
                    wetSample = delayCHNL1.popSample(channel, -1, true); // Second argument of popSample is -1 to use value from setDelay function
                    
                    // No feedback currently for testing purposes
                    delayCHNL1.pushSample(channel, channelData[sample]);//delayCHNL1.pushSample(channel, drySample + wetSample * feedbackFloat);//delayCHNL1.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat);
                    
                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat); // Mix dry sample with delayed sample
                    channelData[sample] *= gainFloat; // Gain
                }
            }
            else // Handles the second channel for stereo input but doesn't run for mono input
            {
                for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                {    
                    drySample = channelData[sample];
                    wetSample = delayCHNL2.popSample(channel, -1, true);
                    
                    // No feedback currently for testing purposes
                    delayCHNL2.pushSample(channel, channelData[sample]);//delayCHNL2.pushSample(channel, drySample + wetSample * feedbackFloat);//delayCHNL2.pushSample(channel, drySample * (1.0f - feedbackFloat) + wetSample * feedbackFloat);
                    
                    channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample * mixFloat);
                    channelData[sample] *= gainFloat;
                }
            }
        }
    }

    //==============================================================================
    juce::AudioProcessorEditor* createEditor() override         { return new juce::GenericAudioProcessorEditor (*this); }
    bool hasEditor() const override                             { return true;   }

    //==============================================================================
    const juce::String getName() const override                 { return "Delay PlugIn"; }
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
        juce::MemoryOutputStream (destData, true).writeFloat (*delay);
        juce::MemoryOutputStream (destData, true).writeFloat (*feedback);
        juce::MemoryOutputStream (destData, true).writeFloat (*mix);
    }

    void setStateInformation (const void* data, int sizeInBytes) override
    {
        gain->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        delay->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        feedback->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        mix->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
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
    juce::AudioParameterFloat* delay;
    juce::AudioParameterFloat* feedback;
    juce::AudioParameterFloat* mix;
    
    float gainFloat;
    float delayFloat;
    float feedbackFloat;
    float mixFloat;
    
    float drySample;
    float wetSample;
    double sampleRate;
    int totalNumInputChannels;
    
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Thiran> delayCHNL1;
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Thiran> delayCHNL2;
    
    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (DelayProcessor)
};
