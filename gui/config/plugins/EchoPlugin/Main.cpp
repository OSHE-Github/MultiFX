#include <JuceHeader.h>
#include "EchoPlugin.h"

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new EchoProcessor();
}