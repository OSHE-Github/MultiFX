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

 name:             EchoPlugin
 version:          1.0.0
 vendor:           JUCE
 website:          oshe.io
 description:      Echo audio plugin.

 dependencies:     juce_audio_basics, juce_audio_devices, juce_audio_formats,
                   juce_audio_plugin_client, juce_audio_processors,
                   juce_audio_utils, juce_core, juce_data_structures, juce_dsp,
                   juce_events, juce_graphics, juce_gui_basics, juce_gui_extra
 exporters:        xcode_mac, vs2022

 moduleFlags:      JUCE_STRICT_REFCOUNTEDPOINTER=1

 type:             AudioProcessor
 mainClass:        EchoProcessor

 useLocalCopy:     1

 END_JUCE_PIP_METADATA

*******************************************************************************/

#pragma once


//==============================================================================
class EchoProcessor final : public juce::AudioProcessor
{
public:

    //==============================================================================
    EchoProcessor()
        : juce::AudioProcessor (BusesProperties().withInput  ("Input",  juce::AudioChannelSet::stereo())
                                                 .withOutput ("Output", juce::AudioChannelSet::stereo()))
    {
        addParameter (gain = new juce::AudioParameterFloat ({ "gain", 1 }, "Gain", 0.0f, 2.0f, 1.0f));
        addParameter (delay = new juce::AudioParameterFloat ({ "delay", 1 }, "Delay", 0.001f, 1.0f, 0.1f)); // Delay is in seconds
        addParameter (feedback = new juce::AudioParameterFloat ({ "feedback", 1 }, "Feedback", 0.0f, 1.0f, 0.2f));
        addParameter (mix = new juce::AudioParameterFloat ({ "mix", 1 }, "Mix", 0.0f, 1.0f, 0.3f));
        addParameter (echo = new juce::AudioParameterInt ({ "echo", 1 }, "Amount of Echoes", 0, 4, 2)); // Zero echoes is pass-through
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
        echoInt = echo->get();
        
        sampleRate = this->getSampleRate();
        totalNumInputChannels  = getTotalNumInputChannels();
        
        delayCHNL1.setDelay (delayFloat * sampleRate);
        delayCHNL2.setDelay (delayFloat * sampleRate);
        
        for (int channel = 0; channel < totalNumInputChannels; ++channel)
        {
            auto* channelData = buffer.getWritePointer (channel);
            
            switch(echoInt)
            {
                case 1: // 1 Echo
                    if (channel == 0)
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            delayInSamples1 = sampleRate * delayFloat;

                            wetSample1 = delayCHNL1.popSample(channel, delayInSamples1, true);
                            
                            drySample = channelData[sample];
                            
                            delayCHNL1.pushSample(channel, (drySample * (1.0f - feedbackFloat)) + (wetSample1 * feedbackFloat)); // Feedback
                            channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample1 * mixFloat); // Mix dry sample with wet sample
                            channelData[sample] *= gainFloat; // Gain
                        }
                    }
                    else // Handles the second channel for stereo input but doesn't run for mono input
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            delayInSamples1 = sampleRate * delayFloat;

                            wetSample1 = delayCHNL2.popSample(channel, delayInSamples1, true);
                            
                            drySample = channelData[sample];
                            
                            delayCHNL2.pushSample(channel, (drySample * (1.0f - feedbackFloat)) + (wetSample1 * feedbackFloat));
                            channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample1 * mixFloat);
                            channelData[sample] *= gainFloat;
                        }
                    }
                    break;
                    
                case 2: // 2 Echoes
                    if (channel == 0)
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            delayInSamples1 = sampleRate * delayFloat * 0.5f;
                            delayInSamples2 = sampleRate * delayFloat;

                            wetSample1 = delayCHNL1.popSample(channel, delayInSamples1, true);
                            wetSample2 = delayCHNL1.popSample(channel, delayInSamples2, true);
                            
                            drySample = channelData[sample];
                            
                            delayCHNL1.pushSample(channel, (drySample * (1.0f - feedbackFloat)) + (wetSample1 * feedbackFloat / 1.5f) + (wetSample2 * feedbackFloat / 3.0f)); // Feedback
                            channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample1 * mixFloat / 1.5f) + (wetSample2 * mixFloat / 3.0f); // Mix
                            channelData[sample] *= gainFloat; // Gain
                        }
                    }
                    else
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            delayInSamples1 = sampleRate * delayFloat * 0.5f;
                            delayInSamples2 = sampleRate * delayFloat;

                            wetSample1 = delayCHNL2.popSample(channel, delayInSamples1, true);
                            wetSample2 = delayCHNL2.popSample(channel, delayInSamples2, true);
                            
                            drySample = channelData[sample];
                            
                            delayCHNL2.pushSample(channel, (drySample * (1.0f - feedbackFloat)) + (wetSample1 * feedbackFloat / 1.5f) + (wetSample2 * feedbackFloat / 3.0f));
                            channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample1 * mixFloat / 1.5f) + (wetSample2 * mixFloat / 3.0f);
                            channelData[sample] *= gainFloat;
                        }
                    }
                    break;
                    
                case 3: // 3 Echoes
                    if (channel == 0)
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            delayInSamples1 = sampleRate * delayFloat * 1.0f / 3.0f;
                            delayInSamples2 = sampleRate * delayFloat * 2.0f / 3.0f;
                            delayInSamples3 = sampleRate * delayFloat;

                            wetSample1 = delayCHNL1.popSample(channel, delayInSamples1, true);
                            wetSample2 = delayCHNL1.popSample(channel, delayInSamples2, true);
                            wetSample3 = delayCHNL1.popSample(channel, delayInSamples3, true);
                            
                            drySample = channelData[sample];
                            
                            delayCHNL1.pushSample(channel, (drySample * (1.0f - feedbackFloat)) + (wetSample1 * feedbackFloat / 2.0f) + (wetSample2 * feedbackFloat / 3.0f) + (wetSample3 * feedbackFloat / 6.0f)); // Feedback
                            channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample1 * mixFloat / 2.0f) + (wetSample2 * mixFloat / 3.0f) + (wetSample3 * mixFloat / 6.0f); // Mix
                            channelData[sample] *= gainFloat; // Gain
                        }
                    }
                    else
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            delayInSamples1 = sampleRate * delayFloat * 1.0f / 3.0f;
                            delayInSamples2 = sampleRate * delayFloat * 2.0f / 3.0f;
                            delayInSamples3 = sampleRate * delayFloat;

                            wetSample1 = delayCHNL2.popSample(channel, delayInSamples1, true);
                            wetSample2 = delayCHNL2.popSample(channel, delayInSamples2, true);
                            wetSample3 = delayCHNL2.popSample(channel, delayInSamples3, true);
                            
                            drySample = channelData[sample];
                            
                            delayCHNL2.pushSample(channel, (drySample * (1.0f - feedbackFloat)) + (wetSample1 * feedbackFloat / 2.0f) + (wetSample2 * feedbackFloat / 3.0f) + (wetSample3 * feedbackFloat / 6.0f));
                            channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample1 * mixFloat / 2.0f) + (wetSample2 * mixFloat / 3.0f) + (wetSample3 * mixFloat / 6.0f);
                            channelData[sample] *= gainFloat;
                        }
                    }
                    break;
                    
                case 4: // 4 Echoes
                    if (channel == 0)
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            delayInSamples1 = sampleRate * delayFloat * 0.25f;
                            delayInSamples2 = sampleRate * delayFloat * 0.5f;
                            delayInSamples3 = sampleRate * delayFloat * 0.75f;
                            delayInSamples4 = sampleRate * delayFloat;

                            wetSample1 = delayCHNL1.popSample(channel, delayInSamples1, true);
                            wetSample2 = delayCHNL1.popSample(channel, delayInSamples2, true);
                            wetSample3 = delayCHNL1.popSample(channel, delayInSamples3, true);
                            wetSample4 = delayCHNL1.popSample(channel, delayInSamples4, true);
                            
                            drySample = channelData[sample];
                            
                            delayCHNL1.pushSample(channel, (drySample * (1.0f - feedbackFloat)) + (wetSample1 * feedbackFloat * 0.4f) + (wetSample2 * feedbackFloat * 0.3f) + (wetSample3 * feedbackFloat * 0.2f) + (wetSample4 * feedbackFloat * 0.1f)); // Feedback
                            channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample1 * mixFloat * 0.4f) + (wetSample2 * mixFloat * 0.3f) + (wetSample3 * mixFloat * 0.2f) + (wetSample4 * mixFloat * 0.1f); // Mix
                            channelData[sample] *= gainFloat; // Gain
                        }
                    }
                    else
                    {
                        for (int sample = 0; sample < buffer.getNumSamples(); ++sample)
                        {
                            delayInSamples1 = sampleRate * delayFloat * 0.25f;
                            delayInSamples2 = sampleRate * delayFloat * 0.5f;
                            delayInSamples3 = sampleRate * delayFloat * 0.75f;
                            delayInSamples4 = sampleRate * delayFloat;

                            wetSample1 = delayCHNL2.popSample(channel, delayInSamples1, true);
                            wetSample2 = delayCHNL2.popSample(channel, delayInSamples2, true);
                            wetSample3 = delayCHNL2.popSample(channel, delayInSamples3, true);
                            wetSample4 = delayCHNL2.popSample(channel, delayInSamples4, true);
                            
                            drySample = channelData[sample];
                            
                            delayCHNL2.pushSample(channel, (drySample * (1.0f - feedbackFloat)) + (wetSample1 * feedbackFloat * 0.4f) + (wetSample2 * feedbackFloat * 0.3f) + (wetSample3 * feedbackFloat * 0.2f) + (wetSample4 * feedbackFloat * 0.1f));
                            channelData[sample] = (drySample * (1.0f - mixFloat)) + (wetSample1 * mixFloat * 0.4f) + (wetSample2 * mixFloat * 0.3f) + (wetSample3 * mixFloat * 0.2f) + (wetSample4 * mixFloat * 0.1f);
                            channelData[sample] *= gainFloat;
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
    const juce::String getName() const override                 { return "Echo PlugIn"; }
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
        juce::MemoryOutputStream (destData, true).writeInt (*echo);
    }

    void setStateInformation (const void* data, int sizeInBytes) override
    {
        gain->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        delay->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        feedback->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        mix->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readFloat());
        echo->setValueNotifyingHost (juce::MemoryInputStream (data, static_cast<size_t> (sizeInBytes), false).readInt());
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
    juce::AudioParameterInt* echo;
    
    float gainFloat;
    float delayFloat;
    float feedbackFloat;
    float mixFloat;
    int echoInt;
    
    double sampleRate;
    int totalNumInputChannels;
    float drySample;
    
    float wetSample1;
    float wetSample2;
    float wetSample3;
    float wetSample4;
    
    int delayInSamples1;
    int delayInSamples2;
    int delayInSamples3;
    int delayInSamples4;
    
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Thiran> delayCHNL1;
    juce::dsp::DelayLine<float, juce::dsp::DelayLineInterpolationTypes::Thiran> delayCHNL2;
    
    //==============================================================================
    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (EchoProcessor)
};
