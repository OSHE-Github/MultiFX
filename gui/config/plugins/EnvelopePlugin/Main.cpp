#include <JuceHeader.h>
#include "EnvelopePlugin.h"

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new EnvelopeProcessor();
}
